"""
Prelude — Simulation Seed Builder (Slice 5)
Converts an experiment brief + agents into simulation seeds for each variant.
"""

# Default journey steps by experiment category
JOURNEY_STEPS_BY_CATEGORY = {
    "onboarding": ["awareness", "signup", "first_use", "habit_formation"],
    "pricing": ["discovery", "evaluation", "price_comparison", "purchase_decision"],
    "retention": ["re-engagement", "value_reminder", "feature_discovery", "commitment"],
    "growth": ["referral_prompt", "sharing", "viral_loop", "network_effect"],
    "conversion": ["landing", "value_prop", "objection_handling", "checkout"],
    "engagement": ["notification", "content_discovery", "interaction", "return_visit"],
}

DEFAULT_STEPS = ["discovery", "evaluation", "decision", "outcome"]


def _journey_steps_for(category: str | None) -> list[str]:
    """Return journey steps appropriate for the experiment category."""
    if category and category.lower() in JOURNEY_STEPS_BY_CATEGORY:
        return JOURNEY_STEPS_BY_CATEGORY[category.lower()]
    return list(DEFAULT_STEPS)


def _build_world_context(experiment: dict) -> dict:
    """Extract world context from the experiment brief."""
    return {
        "product_context": experiment.get("product_context") or "",
        "target_user": experiment.get("target_user") or "",
        "success_metric": experiment.get("success_metric") or "",
        "problem": experiment.get("problem") or "",
        "category": experiment.get("category") or "",
    }


def _serialize_agent(agent: dict) -> dict:
    """Extract the fields needed for a simulation seed agent."""
    return {
        "id": str(agent["id"]),
        "name": agent.get("name", ""),
        "persona_blend": agent.get("persona_blend") or [],
        "traits": agent.get("traits") or {},
        "backstory": agent.get("backstory") or "",
    }


def build_seed(experiment: dict, variant: str, agents: list) -> dict:
    """
    Build a simulation seed for a variant.

    Variant A and B seeds are identical except for the scenario field.

    Args:
        experiment: full experiment row from DB
        variant: "a" or "b"
        agents: list of agent rows from DB

    Returns:
        {scenario, agents, journey_steps, world_context}
    """
    if variant.lower() == "a":
        scenario = experiment.get("variant_a") or ""
    else:
        scenario = experiment.get("variant_b") or ""

    category = experiment.get("category")
    journey_steps = _journey_steps_for(category)

    return {
        "scenario": scenario,
        "agents": [_serialize_agent(a) for a in agents],
        "journey_steps": journey_steps,
        "world_context": _build_world_context(experiment),
    }
