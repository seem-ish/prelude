"""
Prelude — Feature Signal Extractor (v1)
One LLM call at brief submission time.
Extracts behavioral signals from variant descriptions so the simulation
knows HOW a feature affects agents — not just THAT it exists.

Ecommerce-specific: grocery, marketplace, food delivery, quick commerce.
"""

import logging
from .llm_client import call_llm_json, is_available, DEFAULT_EXTRACTION_MODEL

logger = logging.getLogger(__name__)

# ─── Ecommerce vertical context ─────────────────────────────────────────────

VERTICAL_CONTEXT = {
    "online_grocery": {
        "label": "Online Grocery",
        "examples": "Instacart, Amazon Fresh, Walmart+ Grocery",
        "behavioral_signals": [
            "basket_anxiety — worry about missing items or wrong substitutions",
            "weekly_habit_disruption — how much this changes the regular shopping routine",
            "freshness_trust — confidence that perishables arrive in good condition",
            "delivery_slot_urgency — time pressure around available windows",
            "list_completion_rate — can the shopper get everything they need?",
        ],
    },
    "marketplace": {
        "label": "Marketplace",
        "examples": "Amazon, Walmart.com, Target.com, eBay",
        "behavioral_signals": [
            "price_comparison_reflex — instinct to check other sellers/sites",
            "review_dependency — how much buying depends on social proof",
            "return_anxiety — worry about return difficulty if wrong",
            "seller_trust — confidence in third-party seller quality",
            "shipping_expectation — delivery speed as a decision factor",
        ],
    },
    "food_delivery": {
        "label": "Food Delivery",
        "examples": "DoorDash, UberEats, GrubHub, Postmates",
        "behavioral_signals": [
            "delivery_time_sensitivity — tolerance for wait time",
            "surge_price_tolerance — willingness to pay dynamic pricing",
            "reorder_loyalty — tendency to reorder vs explore",
            "menu_overwhelm — paralysis from too many restaurant choices",
            "tip_guilt — social pressure around tipping behavior",
        ],
    },
    "quick_commerce": {
        "label": "Quick Commerce",
        "examples": "Gopuff, Instacart Express, DoorDash DashMart",
        "behavioral_signals": [
            "impulse_threshold — how easily a small need triggers an order",
            "convenience_premium_tolerance — willingness to pay markup for speed",
            "minimum_order_friction — resistance to meeting order minimums",
            "snack_vs_necessity — are they buying wants or needs?",
            "repeat_frequency — how often they'll come back this week",
        ],
    },
    "grocery": {
        "label": "Grocery (general)",
        "examples": "Instacart, Amazon Fresh, Walmart, Kroger",
        "behavioral_signals": [
            "basket_anxiety — worry about missing or wrong items",
            "weekly_habit_disruption — change to regular shopping routine",
            "freshness_trust — confidence in perishable quality",
            "price_sensitivity — attention to per-unit and total basket cost",
            "loyalty_program_pull — influence of rewards/membership on behavior",
        ],
    },
    "ecommerce": {
        "label": "E-commerce (general)",
        "examples": "Any online retail",
        "behavioral_signals": [
            "cart_abandonment_risk — likelihood of leaving before checkout",
            "price_comparison_reflex — tendency to check competitors",
            "trust_barrier — hesitation due to unfamiliarity or risk",
            "shipping_expectation — delivery speed as a decision factor",
            "return_anxiety — worry about post-purchase regret",
        ],
    },
}

# ─── Extraction prompt ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a behavioral research analyst specializing in ecommerce consumer behavior.

Given two A/B test variants for an ecommerce experiment, extract structured behavioral \
signals that predict how different consumer personas will react at each journey step.

You MUST return valid JSON with this exact schema:
{
  "step_impacts": {
    "<step_name>": {"a": <float -1 to 1>, "b": <float -1 to 1>}
  },
  "trait_amplifiers": {
    "<trait_name>": <float 0.5 to 2.0>
  },
  "habit_disruption": <float 0 to 1>,
  "trust_required": <float 0 to 1>,
  "timing_sensitivity": <float 0 to 1>,
  "key_differentiator": "<one sentence: what makes A vs B behaviorally different>",
  "vertical_signals": {
    "<signal_name>": <float 0 to 1>
  }
}

Rules:
- step_impacts: how much each variant helps (+) or hurts (-) at each journey step
- trait_amplifiers: which persona traits matter MORE for this feature (>1) or LESS (<1)
- habit_disruption: 0 = no change to routine, 1 = completely new behavior required
- trust_required: 0 = no trust needed, 1 = high trust barrier
- timing_sensitivity: 0 = works any time, 1 = highly dependent on context/season
- vertical_signals: domain-specific behavioral signals relevant to this experiment
"""


def _build_extraction_prompt(experiment: dict, journey_steps: list[str]) -> str:
    """Build the user prompt for feature signal extraction."""
    category = (experiment.get("category") or "ecommerce").lower()
    vertical = VERTICAL_CONTEXT.get(category, VERTICAL_CONTEXT["ecommerce"])

    signals_list = "\n".join(f"  - {s}" for s in vertical["behavioral_signals"])

    return f"""\
## Experiment Context
- Vertical: {vertical['label']} (e.g. {vertical['examples']})
- Product: {experiment.get('product_context', 'N/A')}
- Target user: {experiment.get('target_user', 'N/A')}
- Problem: {experiment.get('problem', 'N/A')}
- Success metric: {experiment.get('success_metric', 'N/A')}

## Journey Steps
{', '.join(journey_steps)}

## Variant A
{experiment.get('variant_a', 'N/A')}

## Variant B
{experiment.get('variant_b', 'N/A')}

## Domain-Specific Behavioral Signals to Score
{signals_list}

Extract the behavioral signals as JSON."""


# ─── Default fallback (no LLM) ──────────────────────────────────────────────

def _default_signals(journey_steps: list[str]) -> dict:
    """Return neutral feature signals when LLM is unavailable."""
    return {
        "step_impacts": {
            step: {"a": 0.0, "b": 0.05} for step in journey_steps
        },
        "trait_amplifiers": {
            "price_sensitivity": 1.0,
            "trust_baseline": 1.0,
            "decision_speed": 1.0,
            "tech_comfort": 1.0,
            "frustration_threshold": 1.0,
            "research_depth": 1.0,
            "social_influence": 1.0,
            "risk_tolerance": 1.0,
        },
        "habit_disruption": 0.3,
        "trust_required": 0.3,
        "timing_sensitivity": 0.2,
        "key_differentiator": "Variants differ in approach but signals could not be extracted (no LLM configured).",
        "vertical_signals": {},
    }


# ─── Main entry point ───────────────────────────────────────────────────────

def extract_feature_signals(experiment: dict, journey_steps: list[str]) -> dict:
    """
    Extract behavioral signals from experiment variant descriptions.

    Called once at brief submission / before simulation.
    Uses gpt-4o for quality (single call, worth it).
    Falls back to neutral defaults if LLM unavailable.

    Returns:
        {step_impacts, trait_amplifiers, habit_disruption, trust_required,
         timing_sensitivity, key_differentiator, vertical_signals}
    """
    if not is_available():
        logger.info("LLM not available — using default feature signals")
        return _default_signals(journey_steps)

    prompt = _build_extraction_prompt(experiment, journey_steps)

    result = call_llm_json(
        system=SYSTEM_PROMPT,
        user=prompt,
        model=DEFAULT_EXTRACTION_MODEL,
        max_tokens=600,
        temperature=0.2,
    )

    if result is None:
        logger.warning("Feature extraction LLM call failed — using defaults")
        return _default_signals(journey_steps)

    # Validate and fill missing keys
    defaults = _default_signals(journey_steps)
    for key in defaults:
        if key not in result:
            result[key] = defaults[key]

    return result
