"""
Prelude — Prediction Engine (Slice 6)
Generates structured predictions for experiments based on run signals.
"""

import json
import hashlib
from prelude.db import query, execute_returning


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _stable_choice(seed: str, options: list) -> str:
    """Deterministic pick based on a hash of the seed string."""
    idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(options)
    return options[idx]


def _get_experiment(experiment_id: str) -> dict | None:
    rows = query("SELECT * FROM experiments WHERE id = %s", (experiment_id,))
    return dict(rows[0]) if rows else None


def _get_run_signals(experiment_id: str) -> list[dict]:
    """Return all run_signals rows joined through simulation_runs."""
    return query(
        """
        SELECT rs.*
        FROM run_signals rs
        JOIN simulation_runs sr ON sr.id = rs.run_id
        WHERE sr.experiment_id = %s
        ORDER BY rs.id
        """,
        (experiment_id,),
    )


# ─── Segment story builder ───────────────────────────────────────────────────

_PREFERENCE_LABELS = ("strongly_a", "prefers_a", "neutral", "prefers_b", "strongly_b")

_PERSONA_TEMPLATES = [
    {
        "persona": "power_user",
        "narrative_tpl": (
            "Power users who rely on the product daily gravitate toward {pref_label} "
            "because it {reason}. They value efficiency and low friction."
        ),
        "quote_tpl": "I just want it to work fast — {variant} gets out of my way.",
    },
    {
        "persona": "casual_browser",
        "narrative_tpl": (
            "Casual browsers show a {pref_label} lean. "
            "They are drawn to whichever variant feels simpler on first contact, and {reason}."
        ),
        "quote_tpl": "I didn't even notice the difference at first, but {variant} felt easier.",
    },
    {
        "persona": "price_sensitive",
        "narrative_tpl": (
            "Price-sensitive users {pref_label}. "
            "Their decision hinges on perceived value, and {reason}."
        ),
        "quote_tpl": "If {variant} saves me money or time, that's the one I pick.",
    },
    {
        "persona": "new_adopter",
        "narrative_tpl": (
            "First-time users trend {pref_label}. "
            "Onboarding clarity matters most to them, and {reason}."
        ),
        "quote_tpl": "{variant} made me feel like I knew what I was doing right away.",
    },
    {
        "persona": "skeptic",
        "narrative_tpl": (
            "Skeptical users remain {pref_label}. "
            "They distrust novelty and {reason}."
        ),
        "quote_tpl": "I don't trust flashy changes — {variant} feels more trustworthy.",
    },
]


def _build_segment_story(experiment: dict, winner: str, seed: str) -> list[dict]:
    """Generate 3-5 persona segments with preferences and narratives."""
    variant_a_label = experiment.get("variant_a", "Variant A") or "Variant A"
    variant_b_label = experiment.get("variant_b", "Variant B") or "Variant B"
    category = experiment.get("category", "product") or "product"

    # Pick 3-5 personas deterministically
    count = 3 + int(hashlib.sha256(seed.encode()).hexdigest(), 16) % 3
    chosen = _PERSONA_TEMPLATES[:count]

    segments = []
    for i, tpl in enumerate(chosen):
        sub_seed = f"{seed}:seg:{i}"
        pref = _stable_choice(sub_seed, list(_PREFERENCE_LABELS))

        # Determine which variant name to reference in the quote
        if pref in ("strongly_a", "prefers_a"):
            variant_name = variant_a_label[:60]
        elif pref in ("strongly_b", "prefers_b"):
            variant_name = variant_b_label[:60]
        else:
            variant_name = "neither variant clearly"

        # Build a contextual reason based on category
        reasons = {
            "onboarding": "the guided flow reduces cognitive load on first use",
            "pricing": "transparent pricing builds trust and reduces comparison anxiety",
            "engagement": "the interaction pattern aligns with their existing habits",
            "conversion": "clear calls to action reduce decision fatigue",
            "retention": "familiar patterns reinforce the habit loop",
        }
        reason = reasons.get(
            category.lower() if category else "",
            f"the {category or 'product'} experience aligns with their expectations",
        )

        # Percentage of this segment
        pct = 15 + (int(hashlib.sha256(sub_seed.encode()).hexdigest()[:8], 16) % 20)

        segments.append({
            "persona": tpl["persona"],
            "pct": pct,
            "preference": pref,
            "narrative": tpl["narrative_tpl"].format(
                pref_label=pref.replace("_", " "),
                reason=reason,
            ),
            "quote": tpl["quote_tpl"].format(variant=variant_name),
        })

    # Normalise percentages to sum to 100
    total = sum(s["pct"] for s in segments)
    for s in segments:
        s["pct"] = round(s["pct"] / total * 100)
    # Fix rounding so it sums exactly to 100
    diff = 100 - sum(s["pct"] for s in segments)
    segments[0]["pct"] += diff

    return segments


# ─── Main entry point ────────────────────────────────────────────────────────

def generate_prediction(experiment_id: str) -> dict:
    """
    1. Load experiment and run signals from DB.
    2. Generate structured prediction (context-aware mock).
    3. Save to predictions table (upsert).
    4. Return the full prediction dict.
    """

    experiment = _get_experiment(experiment_id)
    if not experiment:
        raise ValueError(f"Experiment {experiment_id} not found")

    signals = _get_run_signals(experiment_id)

    # ── Derive winner & confidence from signals (or heuristic fallback) ──
    seed = f"{experiment_id}:{experiment.get('title', '')}:{experiment.get('category', '')}"

    # If we have actual signals, use adoption data to pick a winner
    if signals:
        a_score, b_score = 0.0, 0.0
        for sig in signals:
            adoption = sig.get("adoption_by_segment")
            if isinstance(adoption, str):
                adoption = json.loads(adoption)
            if adoption and isinstance(adoption, dict):
                for _seg, vals in adoption.items():
                    if isinstance(vals, dict):
                        a_score += vals.get("a", vals.get("variant_a", 0))
                        b_score += vals.get("b", vals.get("variant_b", 0))
        if a_score == b_score == 0:
            winner = _stable_choice(seed, ["a", "b"])
        else:
            winner = "a" if a_score >= b_score else "b"
        gap = abs(a_score - b_score) / max(a_score + b_score, 1)
        confidence = "high" if gap > 0.3 else ("medium" if gap > 0.1 else "low")
    else:
        winner = _stable_choice(seed, ["a", "b"])
        confidence = _stable_choice(seed + ":conf", ["medium", "low"])

    # ── Context-aware text generation ────────────────────────────────────
    title = experiment.get("title", "this experiment") or "this experiment"
    category = experiment.get("category", "product") or "product"
    problem = experiment.get("problem", "") or ""
    variant_a = experiment.get("variant_a", "Variant A") or "Variant A"
    variant_b = experiment.get("variant_b", "Variant B") or "Variant B"
    target_user = experiment.get("target_user", "users") or "users"
    success_metric = experiment.get("success_metric", "engagement") or "engagement"
    winner_label = variant_a if winner == "a" else variant_b

    confidence_rationale = (
        f"Based on signal analysis across {len(signals) or 'simulated'} run(s), "
        f"Variant {'A' if winner == 'a' else 'B'} ({winner_label[:80]}) shows a "
        f"{'clear' if confidence == 'high' else 'moderate' if confidence == 'medium' else 'marginal'} "
        f"advantage in {success_metric} among {target_user}. "
        f"{'Signal consistency across segments reinforces this call.' if confidence == 'high' else 'Some segments diverge, introducing uncertainty.' if confidence == 'medium' else 'The gap is narrow and could reverse with different user mixes.'}"
    )

    mechanism = (
        f"The winning variant succeeds because it directly addresses the core tension "
        f"in the {category} context: {problem[:120] + '...' if len(problem) > 120 else problem or 'the identified user friction'}. "
        f"Specifically, {winner_label[:80]} reduces friction for {target_user} by aligning "
        f"with their existing mental model. "
        f"This creates a compounding effect — lower initial resistance leads to deeper "
        f"exploration, which in turn drives {success_metric}. "
        f"The causal chain is: reduced cognitive load → higher trial engagement → "
        f"stronger habit formation → measurable lift in {success_metric}."
    )

    key_risk = (
        f"The primary risk is segment heterogeneity: while the aggregate favors "
        f"{'Variant A' if winner == 'a' else 'Variant B'}, at least one persona cluster "
        f"shows a {'neutral' if confidence == 'high' else 'contrary'} signal. "
        f"If the real-world user mix skews toward that segment, the predicted winner "
        f"could underperform. Additionally, the {category} category is sensitive to "
        f"external timing factors (seasonality, competitor moves) not captured in simulation."
    )

    watch_items = [
        f"Track {success_metric} daily for first 7 days — expect {'≥5%' if confidence == 'high' else '2-5%' if confidence == 'medium' else '1-2%'} lift for the winning variant",
        f"Monitor drop-off rate at the primary interaction point; a spike above 15% suggests the mechanism is not transferring to production",
        f"Segment {success_metric} by {target_user} cohort — if the skeptic/new-user split diverges by >10pp, revisit the prediction",
    ]

    recommended_mod = (
        f"Consider softening the losing variant's weakest element rather than "
        f"discarding it entirely — hybrid approaches can capture both segments. "
        f"If Variant {'A' if winner == 'a' else 'B'} wins in production, run a follow-up "
        f"test isolating the specific UI element (not the full variant) to confirm which "
        f"component drives the lift. "
        f"Also set a hold-out group at 5% to measure long-term {success_metric} decay."
    )

    segment_story = _build_segment_story(experiment, winner, seed)

    # ── Persist (upsert) ─────────────────────────────────────────────────
    prediction_row = execute_returning(
        """
        INSERT INTO predictions
            (experiment_id, winner, confidence, confidence_rationale,
             segment_story, mechanism, key_risk, watch_items, recommended_mod)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (experiment_id) DO UPDATE SET
            winner              = EXCLUDED.winner,
            confidence          = EXCLUDED.confidence,
            confidence_rationale = EXCLUDED.confidence_rationale,
            segment_story       = EXCLUDED.segment_story,
            mechanism           = EXCLUDED.mechanism,
            key_risk            = EXCLUDED.key_risk,
            watch_items         = EXCLUDED.watch_items,
            recommended_mod     = EXCLUDED.recommended_mod,
            created_at          = NOW()
        RETURNING *
        """,
        (
            str(experiment_id),
            winner,
            confidence,
            confidence_rationale,
            json.dumps(segment_story),
            mechanism,
            key_risk,
            json.dumps(watch_items),
            recommended_mod,
        ),
    )

    return _serialize_prediction(prediction_row)


def _serialize_prediction(row: dict) -> dict:
    """Make a prediction row JSON-safe."""
    out = dict(row)
    for k, v in out.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "__str__") and type(v).__name__ == "UUID":
            out[k] = str(v)
    # Ensure JSONB fields are dicts/lists, not strings
    for field in ("segment_story", "watch_items"):
        if isinstance(out.get(field), str):
            out[field] = json.loads(out[field])
    return out
