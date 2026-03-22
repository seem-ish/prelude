"""
Prelude — Simulation Orchestrator (Slice 5)
Runs both A/B variants and generates synthetic agent events.
"""

import json
import random
import hashlib
from datetime import datetime, timedelta, timezone

from prelude.db import query, execute, execute_returning
from .seed_builder import build_seed
from .signal_extractor import extract_signals

# ─── Event content templates ────────────────────────────────────────────────

REACTION_TEMPLATES = {
    "positive": [
        "This feels intuitive. I can see how this fits my workflow.",
        "I like the direction — it addresses a real pain point for me.",
        "Interesting approach. I'd want to try this more.",
        "This resonates with what I've been looking for.",
        "Clean experience, I didn't have to think too much.",
    ],
    "neutral": [
        "Not sure how this is different from what I already use.",
        "It works, but nothing jumps out as special.",
        "I need more time to decide if this adds value.",
        "Functional, but the value proposition isn't clear yet.",
        "I can see the idea, but execution feels half-baked.",
    ],
    "negative": [
        "This is confusing — I'm not sure what I'm supposed to do next.",
        "Too many steps. I'd probably drop off at this point.",
        "This feels like it was designed without talking to actual users.",
        "I don't trust this enough to give it my real data.",
        "Frustrating experience. I'd go back to my current solution.",
    ],
}

DECISION_TEMPLATES = {
    "positive": [
        "I'd continue using this. It saves me time.",
        "I'm willing to recommend this to my team.",
        "I'd switch from my current tool for this.",
        "Worth the investment — clear ROI for me.",
        "I'd sign up for the paid plan.",
    ],
    "neutral": [
        "I'd keep it installed but probably forget about it.",
        "Maybe I'd use it once a month at most.",
        "I'd need to see more features before committing.",
        "I'd try the free tier but not pay for it.",
        "I'd wait to see what others think first.",
    ],
    "negative": [
        "I'm abandoning this — not worth my time.",
        "I'd uninstall and go back to the old way.",
        "No chance I'd pay for this.",
        "I'd warn others to avoid this.",
        "This would sit unused in my app drawer.",
    ],
}

EMOTION_TEMPLATES = {
    "positive": [
        "Feeling excited about the possibilities here.",
        "Pleasantly surprised — this is better than expected.",
        "Relief — finally something that gets it right.",
        "Curious to explore more features.",
        "Confident this could solve my problem.",
    ],
    "neutral": [
        "Feeling indifferent — it's fine, I guess.",
        "Mildly curious but not compelled.",
        "A bit confused about the next steps.",
        "Cautiously interested.",
        "Feeling uncertain about whether this is for me.",
    ],
    "negative": [
        "Frustrated with the unnecessary complexity.",
        "Anxious about data privacy here.",
        "Annoyed — this wasted my time.",
        "Disappointed — the promise didn't match reality.",
        "Feeling overwhelmed by too many options.",
    ],
}

CONTENT_BY_TYPE = {
    "reaction": REACTION_TEMPLATES,
    "decision": DECISION_TEMPLATES,
    "emotion": EMOTION_TEMPLATES,
}


# ─── Synthetic event generation ─────────────────────────────────────────────

def _agent_disposition(agent: dict) -> float:
    """
    Compute a base disposition score for an agent based on traits.
    Returns a value between -0.3 and 0.3 that biases their sentiment.
    """
    traits = agent.get("traits") or {}
    score = 0.0

    # High trust → more positive
    trust = traits.get("trust_baseline", 0.5)
    score += (trust - 0.5) * 0.4

    # Low frustration threshold → more negative
    frustration = traits.get("frustration_threshold", 0.5)
    score -= (0.5 - frustration) * 0.3

    # High openness → more positive
    openness = traits.get("openness_to_change", 0.5)
    score += (openness - 0.5) * 0.2

    # Clamp
    return max(-0.3, min(0.3, score))


def _pick_content(event_type: str, sentiment: float) -> str:
    """Pick a content string based on event type and sentiment."""
    templates = CONTENT_BY_TYPE.get(event_type, REACTION_TEMPLATES)
    if sentiment > 0.25:
        pool = templates["positive"]
    elif sentiment < -0.25:
        pool = templates["negative"]
    else:
        pool = templates["neutral"]
    return random.choice(pool)


def _deterministic_seed(experiment_id: str, variant: str) -> int:
    """Create a deterministic random seed from experiment+variant for reproducibility."""
    h = hashlib.sha256(f"{experiment_id}:{variant}".encode()).hexdigest()
    return int(h[:8], 16)


def _generate_events_for_variant(seed: dict, variant: str, experiment_id: str) -> list:
    """
    Generate synthetic agent events for one variant.
    Returns a list of event dicts ready for DB insertion.
    """
    rng = random.Random(_deterministic_seed(experiment_id, variant))
    agents = seed["agents"]
    steps = seed["journey_steps"]
    events = []

    # Variant B gets a slight positive nudge (simulating the "new" variant)
    variant_bias = 0.05 if variant == "b" else 0.0

    for agent in agents:
        disposition = _agent_disposition(agent) + variant_bias
        traits = agent.get("traits") or {}
        frustration_threshold = traits.get("frustration_threshold", 0.5)

        abandoned = False
        for step_idx, step in enumerate(steps):
            if abandoned:
                break

            # Each agent generates 1-2 events per step
            n_events = rng.choices([1, 2], weights=[0.6, 0.4])[0]
            for _ in range(n_events):
                event_type = rng.choice(["reaction", "decision", "emotion"])

                # Sentiment: base disposition + per-step noise + step decay
                step_decay = -0.05 * step_idx  # slight friction over journey
                noise = rng.gauss(0, 0.2)
                sentiment = disposition + step_decay + noise
                sentiment = max(-1.0, min(1.0, round(sentiment, 3)))

                content = _pick_content(event_type, sentiment)

                events.append({
                    "agent_id": agent["id"],
                    "agent_name": agent["name"],
                    "step": step,
                    "step_index": step_idx,
                    "event_type": event_type,
                    "content": content,
                    "sentiment": sentiment,
                })

                # Frustration-based abandonment check
                if sentiment < -0.5 and frustration_threshold < 0.4:
                    if rng.random() < 0.4:
                        events.append({
                            "agent_id": agent["id"],
                            "agent_name": agent["name"],
                            "step": step,
                            "step_index": step_idx,
                            "event_type": "decision",
                            "content": "I'm abandoning this — not worth my time.",
                            "sentiment": round(sentiment - 0.2, 3),
                        })
                        abandoned = True
                        break

    # Ensure we have at least 15 events (pad if tiny population)
    while len(events) < 15:
        agent = rng.choice(agents)
        step = rng.choice(steps)
        step_idx = steps.index(step)
        event_type = rng.choice(["reaction", "decision", "emotion"])
        sentiment = round(rng.gauss(_agent_disposition(agent), 0.25), 3)
        sentiment = max(-1.0, min(1.0, sentiment))
        events.append({
            "agent_id": agent["id"],
            "agent_name": agent["name"],
            "step": step,
            "step_index": step_idx,
            "event_type": event_type,
            "content": _pick_content(event_type, sentiment),
            "sentiment": sentiment,
        })

    # Cap at 25 events if too many
    if len(events) > 25:
        events = rng.sample(events, 25)
        events.sort(key=lambda e: e["step_index"])

    # Assign timestamps
    base_time = datetime.now(timezone.utc)
    for i, event in enumerate(events):
        event["timestamp"] = base_time + timedelta(seconds=i * 2)

    return events


# ─── DB helpers ──────────────────────────────────────────────────────────────

def _create_run(experiment_id: str, variant: str, agent_count: int) -> dict:
    """Insert a simulation_runs row and return it."""
    return execute_returning(
        """
        INSERT INTO simulation_runs (experiment_id, variant, agent_count, status, started_at)
        VALUES (%s, %s, %s, 'running', NOW())
        RETURNING *
        """,
        (experiment_id, variant, agent_count),
    )


def _complete_run(run_id: str, events_generated: int):
    """Mark a run as completed."""
    execute(
        """
        UPDATE simulation_runs
        SET status = 'completed', completed_at = NOW(), raw_output = %s
        WHERE id = %s
        """,
        (json.dumps({"events_generated": events_generated}), str(run_id)),
    )


def _fail_run(run_id: str, error: str):
    """Mark a run as failed."""
    execute(
        """
        UPDATE simulation_runs
        SET status = 'failed', completed_at = NOW(), error_log = %s
        WHERE id = %s
        """,
        (error, str(run_id)),
    )


def _insert_events(run_id: str, events: list):
    """Bulk-insert agent events."""
    for ev in events:
        execute(
            """
            INSERT INTO agent_events (run_id, agent_id, event_type, content, sentiment, journey_step, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(run_id),
                ev["agent_id"],
                ev["event_type"],
                ev["content"],
                ev["sentiment"],
                ev["step"],
                ev["timestamp"],
            ),
        )


def _save_signals(run_id: str, signals: dict):
    """Insert run signals."""
    execute(
        """
        INSERT INTO run_signals (run_id, adoption_by_segment, friction_heatmap, sentiment_arc, top_quotes, behavioral_patterns)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (run_id) DO UPDATE SET
            adoption_by_segment = EXCLUDED.adoption_by_segment,
            friction_heatmap = EXCLUDED.friction_heatmap,
            sentiment_arc = EXCLUDED.sentiment_arc,
            top_quotes = EXCLUDED.top_quotes,
            behavioral_patterns = EXCLUDED.behavioral_patterns
        """,
        (
            str(run_id),
            json.dumps(signals.get("adoption_by_segment", {})),
            json.dumps(signals.get("friction_heatmap", [])),
            json.dumps(signals.get("sentiment_arc", {})),
            json.dumps(signals.get("top_quotes", [])),
            json.dumps(signals.get("behavioral_patterns", [])),
        ),
    )


# ─── Main entry point ───────────────────────────────────────────────────────

def run_ab_simulation(experiment_id: str) -> dict:
    """
    Run both A and B simulation variants for an experiment.

    1. Load experiment and agents from DB
    2. Build seeds for A and B
    3. Simulate both variants (generate synthetic events)
    4. Write events to DB
    5. Extract signals
    6. Return run results
    """
    # 1. Load experiment
    rows = query("SELECT * FROM experiments WHERE id = %s", (experiment_id,))
    if not rows:
        raise ValueError(f"Experiment {experiment_id} not found")
    experiment = dict(rows[0])

    # Load agents
    agents = query(
        "SELECT * FROM agents WHERE experiment_id = %s ORDER BY created_at",
        (experiment_id,),
    )
    if not agents:
        raise ValueError(f"No agents found for experiment {experiment_id}. Build a population first.")

    results = {}

    for variant in ["a", "b"]:
        # 2. Build seed
        seed = build_seed(experiment, variant, agents)

        # 3. Create run record
        run = _create_run(experiment_id, variant, len(agents))
        run_id = str(run["id"])

        try:
            # 4. Generate synthetic events
            events = _generate_events_for_variant(seed, variant, experiment_id)

            # 5. Write events to DB
            _insert_events(run_id, events)

            # 6. Mark complete
            _complete_run(run_id, len(events))

            results[variant] = {
                "run_id": run_id,
                "status": "completed",
                "events_generated": len(events),
                "events": events,
            }

        except Exception as exc:
            _fail_run(run_id, str(exc))
            results[variant] = {
                "run_id": run_id,
                "status": "failed",
                "error": str(exc),
            }

    # 7. Extract signals from both variants
    events_a = results.get("a", {}).get("events", [])
    events_b = results.get("b", {}).get("events", [])

    signals = extract_signals(events_a, events_b, experiment)

    # Save signals for both runs
    for variant in ["a", "b"]:
        run_id = results.get(variant, {}).get("run_id")
        if run_id:
            _save_signals(run_id, signals)

    # Update experiment status
    execute(
        "UPDATE experiments SET status = 'simulated', updated_at = NOW() WHERE id = %s",
        (experiment_id,),
    )

    return {
        "experiment_id": experiment_id,
        "variant_a": {
            "run_id": results["a"]["run_id"],
            "status": results["a"]["status"],
            "events_generated": results["a"].get("events_generated", 0),
        },
        "variant_b": {
            "run_id": results["b"]["run_id"],
            "status": results["b"]["status"],
            "events_generated": results["b"].get("events_generated", 0),
        },
        "signals": signals,
    }
