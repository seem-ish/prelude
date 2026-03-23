"""
Prelude — Simulation Orchestrator (v1)
LLM-driven per-step agent decisions with dynamic state accumulation.
Falls back to v0 algorithmic mode when no OPENAI_API_KEY is set.

v0: sentiment = disposition + step_decay + noise (static math)
v1: per-step LLM call → sentiment + VoC quote + state deltas (dynamic)
"""

import json
import random
import hashlib
import logging
from datetime import datetime, timedelta, timezone

from prelude.db import query, execute, execute_returning
from .seed_builder import build_seed
from .signal_extractor import extract_signals
from .feature_extractor import extract_feature_signals
from .voc_formatter import format_voc
from .llm_client import call_llm_json, is_available as llm_available

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# v0 TEMPLATES (fallback when LLM unavailable)
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# v1: LLM-DRIVEN PER-STEP SIMULATION
# ══════════════════════════════════════════════════════════════════════════════

AGENT_SYSTEM_PROMPT = """\
You are simulating a real ecommerce consumer reacting to a product experience.
You must stay in character as this specific persona throughout the journey.

## Your persona
Name: {name}
Cluster: {cluster}
Description: {description}
Backstory: {backstory}

## Your traits (0-1 scale)
{traits_block}

## Your motivations
{motivations}

## Your fears
{fears}

## Ecommerce context
Category: {category}
Product: {product_context}

## Feature being tested
{scenario}

## Feature behavioral signals
- Habit disruption: {habit_disruption}/1.0
- Trust required: {trust_required}/1.0
- Key differentiator: {key_differentiator}
{vertical_signals_block}

You MUST respond with valid JSON:
{{
  "sentiment": <float -1.0 to 1.0>,
  "quote": "<first-person quote, 1-2 sentences, in character>",
  "action": "<what you do: browse, add_to_cart, hesitate, compare, abandon, proceed, purchase>",
  "trust_delta": <float -0.3 to 0.3>,
  "frustration_delta": <float -0.2 to 0.3>,
  "momentum_delta": <float -0.3 to 0.3>
}}

Rules:
- quote MUST be first-person, specific to the feature, and reflect your persona
- Do NOT use generic phrases. Reference specific ecommerce behaviors (prices, delivery, cart, etc.)
- Your response should reflect accumulated state — if frustrated, show it escalating
- If trust is low and trust_required is high, be MORE skeptical
- If habit_disruption is high and you're a cautious persona, resist more
"""

STEP_USER_PROMPT = """\
## Journey Step {step_idx}/{total_steps}: {step_name}

## Your accumulated state
- Trust balance: {trust_balance:.2f} (started at 0.50)
- Frustration level: {frustration_level:.2f} (0 = calm, 1 = furious)
- Momentum: {momentum:.2f} (negative = stalling, positive = moving toward purchase)
- Investment: {investment:.2f} (how much you've committed to this journey so far)

## Step impact from feature signals
This feature affects this step: A={step_impact_a:+.2f}, B={step_impact_b:+.2f}

{previous_summary}

React to this step as your persona. What do you feel, think, and do?"""


def _build_traits_block(traits: dict) -> str:
    """Format traits for the prompt."""
    lines = []
    for k, v in sorted(traits.items()):
        label = k.replace("_", " ").title()
        bar = "█" * int(v * 10) + "░" * (10 - int(v * 10))
        lines.append(f"- {label}: {bar} {v:.2f}")
    return "\n".join(lines)


def _build_vertical_signals_block(signals: dict) -> str:
    """Format vertical-specific signals."""
    if not signals:
        return ""
    lines = ["## Domain-specific signals"]
    for k, v in sorted(signals.items()):
        label = k.replace("_", " ").title()
        lines.append(f"- {label}: {v:.2f}")
    return "\n".join(lines)


def _get_persona_info(agent: dict) -> dict:
    """Extract persona details from agent for prompt building."""
    blend = agent.get("persona_blend") or []
    if isinstance(blend, list) and blend:
        primary = max(blend, key=lambda b: b.get("influence", 0))
        slug = primary.get("slug", "")
        # Try to get full persona info from library
        try:
            from prelude.agents.persona_library import PERSONA_LIBRARY
            for p in PERSONA_LIBRARY:
                if p["slug"] == slug:
                    return {
                        "name": p.get("name", agent.get("name", "Consumer")),
                        "cluster": p.get("cluster", "unknown"),
                        "description": p.get("description", ""),
                        "motivations": ", ".join(p.get("motivations", [])),
                        "fears": ", ".join(p.get("fears", [])),
                    }
        except Exception:
            pass
    return {
        "name": agent.get("name", "Consumer"),
        "cluster": "unknown",
        "description": agent.get("backstory", "An ecommerce shopper."),
        "motivations": "",
        "fears": "",
    }


def _llm_generate_events_for_variant(
    seed: dict,
    variant: str,
    experiment_id: str,
    feature_signals: dict,
) -> list:
    """
    v1: LLM-driven per-step agent simulation with dynamic state accumulation.
    Each agent reacts to each step via an LLM call, accumulating state.
    """
    agents = seed["agents"]
    steps = seed["journey_steps"]
    scenario = seed["scenario"]
    world = seed["world_context"]
    events = []

    category = world.get("category", "ecommerce")
    product_context = world.get("product_context", "")

    step_impacts = feature_signals.get("step_impacts", {})
    habit_disruption = feature_signals.get("habit_disruption", 0.3)
    trust_required = feature_signals.get("trust_required", 0.3)
    key_diff = feature_signals.get("key_differentiator", "")
    vertical_sigs = feature_signals.get("vertical_signals", {})

    base_time = datetime.now(timezone.utc)
    event_counter = 0

    for agent in agents:
        traits = agent.get("traits") or {}
        persona = _get_persona_info(agent)

        # Build the system prompt for this agent (same across all steps)
        system = AGENT_SYSTEM_PROMPT.format(
            name=persona["name"],
            cluster=persona["cluster"],
            description=persona["description"],
            backstory=agent.get("backstory", ""),
            traits_block=_build_traits_block(traits),
            motivations=persona["motivations"],
            fears=persona["fears"],
            category=category,
            product_context=product_context,
            scenario=scenario,
            habit_disruption=habit_disruption,
            trust_required=trust_required,
            key_differentiator=key_diff,
            vertical_signals_block=_build_vertical_signals_block(vertical_sigs),
        )

        # Initialize dynamic state
        state = {
            "trust_balance": traits.get("trust_baseline", 0.5),
            "frustration_level": 0.0,
            "momentum": 0.0,
            "investment": 0.0,
        }

        previous_summary = "This is the first step — no prior experience yet."
        abandoned = False

        for step_idx, step in enumerate(steps):
            if abandoned:
                break

            # Get step impact for this variant
            impact = step_impacts.get(step, {})
            impact_a = impact.get("a", 0.0) if isinstance(impact, dict) else 0.0
            impact_b = impact.get("b", 0.0) if isinstance(impact, dict) else 0.0

            user_prompt = STEP_USER_PROMPT.format(
                step_idx=step_idx + 1,
                total_steps=len(steps),
                step_name=step.replace("_", " ").title(),
                trust_balance=state["trust_balance"],
                frustration_level=state["frustration_level"],
                momentum=state["momentum"],
                investment=state["investment"],
                step_impact_a=impact_a,
                step_impact_b=impact_b,
                previous_summary=previous_summary,
            )

            result = call_llm_json(
                system=system,
                user=user_prompt,
                max_tokens=200,
                temperature=0.7,
            )

            if result is None:
                # LLM call failed — fall back to v0 math for this step
                logger.warning("LLM call failed for agent %s step %s — using v0 fallback",
                               agent["id"], step)
                result = _v0_fallback_step(agent, step_idx, variant)

            sentiment = max(-1.0, min(1.0, float(result.get("sentiment", 0.0))))
            quote = result.get("quote", "No response.")
            action = result.get("action", "proceed")

            # Update dynamic state
            trust_d = max(-0.3, min(0.3, float(result.get("trust_delta", 0.0))))
            frust_d = max(-0.2, min(0.3, float(result.get("frustration_delta", 0.0))))
            mom_d = max(-0.3, min(0.3, float(result.get("momentum_delta", 0.0))))

            state["trust_balance"] = max(0.0, min(1.0, state["trust_balance"] + trust_d))
            state["frustration_level"] = max(0.0, min(1.0, state["frustration_level"] + frust_d))
            state["momentum"] = max(-1.0, min(1.0, state["momentum"] + mom_d))
            state["investment"] = min(1.0, state["investment"] + 0.1 + max(0, mom_d))

            events.append({
                "agent_id": agent["id"],
                "agent_name": agent.get("name", ""),
                "step": step,
                "step_index": step_idx,
                "event_type": "reaction",
                "content": quote,
                "sentiment": round(sentiment, 3),
                "action": action,
                "state_snapshot": {**state},
                "timestamp": base_time + timedelta(seconds=event_counter * 2),
            })
            event_counter += 1

            # Build summary for next step
            previous_summary = (
                f"Previous step ({step.replace('_', ' ')}): "
                f"sentiment={sentiment:+.2f}, action={action}, "
                f"said: \"{quote[:80]}...\""
                if len(quote) > 80
                else f"Previous step ({step.replace('_', ' ')}): "
                     f"sentiment={sentiment:+.2f}, action={action}, "
                     f"said: \"{quote}\""
            )

            # Abandonment check
            if action == "abandon" or (
                state["frustration_level"] > 0.8
                and sentiment < -0.5
                and traits.get("frustration_threshold", 0.5) < 0.4
            ):
                events.append({
                    "agent_id": agent["id"],
                    "agent_name": agent.get("name", ""),
                    "step": step,
                    "step_index": step_idx,
                    "event_type": "decision",
                    "content": f"I'm done. {quote}" if action == "abandon" else "I'm abandoning this — not worth my time.",
                    "sentiment": round(min(sentiment - 0.2, -0.5), 3),
                    "action": "abandon",
                    "state_snapshot": {**state},
                    "timestamp": base_time + timedelta(seconds=event_counter * 2),
                })
                event_counter += 1
                abandoned = True

    return events


def _v0_fallback_step(agent: dict, step_idx: int, variant: str) -> dict:
    """Generate a v0-style result when LLM call fails."""
    traits = agent.get("traits") or {}
    disposition = _agent_disposition(agent)
    variant_bias = 0.05 if variant == "b" else 0.0
    noise = random.gauss(0, 0.2)
    step_decay = -0.05 * step_idx
    sentiment = max(-1.0, min(1.0, disposition + variant_bias + step_decay + noise))

    content = _pick_content("reaction", sentiment)
    return {
        "sentiment": round(sentiment, 3),
        "quote": content,
        "action": "abandon" if sentiment < -0.6 else "proceed" if sentiment > -0.2 else "hesitate",
        "trust_delta": 0.0,
        "frustration_delta": max(0, -sentiment * 0.1),
        "momentum_delta": sentiment * 0.1,
    }


# ══════════════════════════════════════════════════════════════════════════════
# v0: ALGORITHMIC FALLBACK (no LLM needed)
# ══════════════════════════════════════════════════════════════════════════════

def _agent_disposition(agent: dict) -> float:
    """Compute base disposition from traits. Returns -0.3 to 0.3."""
    traits = agent.get("traits") or {}
    score = 0.0
    trust = traits.get("trust_baseline", 0.5)
    score += (trust - 0.5) * 0.4
    frustration = traits.get("frustration_threshold", 0.5)
    score -= (0.5 - frustration) * 0.3
    openness = traits.get("openness_to_change", 0.5)
    score += (openness - 0.5) * 0.2
    return max(-0.3, min(0.3, score))


def _pick_content(event_type: str, sentiment: float) -> str:
    """Pick a content string based on event type and sentiment (v0)."""
    templates = CONTENT_BY_TYPE.get(event_type, REACTION_TEMPLATES)
    if sentiment > 0.25:
        pool = templates["positive"]
    elif sentiment < -0.25:
        pool = templates["negative"]
    else:
        pool = templates["neutral"]
    return random.choice(pool)


def _deterministic_seed(experiment_id: str, variant: str) -> int:
    h = hashlib.sha256(f"{experiment_id}:{variant}".encode()).hexdigest()
    return int(h[:8], 16)


def _v0_generate_events_for_variant(seed: dict, variant: str, experiment_id: str) -> list:
    """v0 algorithmic event generation — no LLM calls."""
    rng = random.Random(_deterministic_seed(experiment_id, variant))
    agents = seed["agents"]
    steps = seed["journey_steps"]
    events = []
    variant_bias = 0.05 if variant == "b" else 0.0

    for agent in agents:
        disposition = _agent_disposition(agent) + variant_bias
        traits = agent.get("traits") or {}
        frustration_threshold = traits.get("frustration_threshold", 0.5)
        abandoned = False

        for step_idx, step in enumerate(steps):
            if abandoned:
                break
            n_events = rng.choices([1, 2], weights=[0.6, 0.4])[0]
            for _ in range(n_events):
                event_type = rng.choice(["reaction", "decision", "emotion"])
                step_decay = -0.05 * step_idx
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

    if len(events) > 25:
        events = rng.sample(events, 25)
        events.sort(key=lambda e: e["step_index"])

    base_time = datetime.now(timezone.utc)
    for i, event in enumerate(events):
        event["timestamp"] = base_time + timedelta(seconds=i * 2)
    return events


# ══════════════════════════════════════════════════════════════════════════════
# DB HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _create_run(experiment_id: str, variant: str, agent_count: int, mode: str = "v0") -> dict:
    return execute_returning(
        """
        INSERT INTO simulation_runs (experiment_id, variant, agent_count, status, started_at, raw_output)
        VALUES (%s, %s, %s, 'running', NOW(), %s)
        RETURNING *
        """,
        (experiment_id, variant, agent_count, json.dumps({"mode": mode})),
    )


def _complete_run(run_id: str, events_generated: int, mode: str = "v0"):
    execute(
        """
        UPDATE simulation_runs
        SET status = 'completed', completed_at = NOW(), raw_output = %s
        WHERE id = %s
        """,
        (json.dumps({"events_generated": events_generated, "mode": mode}), str(run_id)),
    )


def _fail_run(run_id: str, error: str):
    execute(
        """
        UPDATE simulation_runs
        SET status = 'failed', completed_at = NOW(), error_log = %s
        WHERE id = %s
        """,
        (error, str(run_id)),
    )


def _insert_events(run_id: str, events: list):
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


def _save_voc(run_id: str, voc: dict):
    """Save VoC output alongside run signals."""
    execute(
        """
        UPDATE run_signals SET voc_output = %s
        WHERE run_id = %s
        """,
        (json.dumps(voc), str(run_id)),
    )


def _save_feature_signals(experiment_id: str, feature_signals: dict):
    """Store extracted feature signals on the experiment."""
    execute(
        """
        UPDATE experiments SET feature_signals = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (json.dumps(feature_signals), experiment_id),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def run_ab_simulation(experiment_id: str) -> dict:
    """
    Run both A and B simulation variants for an experiment.

    v1 mode (OPENAI_API_KEY set):
      1. Extract feature signals from variant descriptions (1 LLM call)
      2. Per-step LLM calls per agent with dynamic state accumulation
      3. Generate VoC output structured by segment

    v0 mode (no API key):
      Falls back to algorithmic simulation (same as before)
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

    # Determine mode
    use_llm = llm_available()
    mode = "v1" if use_llm else "v0"
    logger.info("Running simulation in %s mode for experiment %s (%d agents)",
                mode, experiment_id, len(agents))

    # 2. Extract feature signals (v1 only, but store anyway)
    seed_a = build_seed(experiment, "a", agents)
    journey_steps = seed_a["journey_steps"]
    feature_signals = extract_feature_signals(experiment, journey_steps)
    _save_feature_signals(experiment_id, feature_signals)

    results = {}

    for variant in ["a", "b"]:
        seed = build_seed(experiment, variant, agents)
        run = _create_run(experiment_id, variant, len(agents), mode=mode)
        run_id = str(run["id"])

        try:
            if use_llm:
                events = _llm_generate_events_for_variant(
                    seed, variant, experiment_id, feature_signals
                )
            else:
                events = _v0_generate_events_for_variant(seed, variant, experiment_id)

            _insert_events(run_id, events)
            _complete_run(run_id, len(events), mode=mode)

            results[variant] = {
                "run_id": run_id,
                "status": "completed",
                "events_generated": len(events),
                "events": events,
            }

        except Exception as exc:
            logger.exception("Simulation failed for variant %s", variant)
            _fail_run(run_id, str(exc))
            results[variant] = {
                "run_id": run_id,
                "status": "failed",
                "error": str(exc),
            }

    # 3. Extract analytical signals from both variants
    events_a = results.get("a", {}).get("events", [])
    events_b = results.get("b", {}).get("events", [])

    signals = extract_signals(events_a, events_b, experiment)

    # 4. Build VoC output (v1 gets real quotes, v0 gets template-based)
    agents_by_id = {str(a["id"]): dict(a) for a in agents}
    voc = format_voc(events_a, events_b, agents_by_id)

    # Save signals and VoC for both runs
    for variant in ["a", "b"]:
        run_id = results.get(variant, {}).get("run_id")
        if run_id:
            _save_signals(run_id, signals)
            _save_voc(run_id, voc)

    # Update experiment status
    execute(
        "UPDATE experiments SET status = 'simulated', updated_at = NOW() WHERE id = %s",
        (experiment_id,),
    )

    return {
        "experiment_id": experiment_id,
        "mode": mode,
        "feature_signals": feature_signals,
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
        "voc": voc,
    }
