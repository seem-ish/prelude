"""
Prelude — Simulation Seed Builder (Slice 5)
Converts an experiment brief + agents into simulation seeds for each variant.
"""

# Default journey steps by experiment category
JOURNEY_STEPS_BY_CATEGORY = {
    # Generic categories
    "onboarding": ["awareness", "signup", "first_use", "habit_formation"],
    "pricing": ["discovery", "evaluation", "price_comparison", "purchase_decision"],
    "retention": ["re-engagement", "value_reminder", "feature_discovery", "commitment"],
    "growth": ["referral_prompt", "sharing", "viral_loop", "network_effect"],
    "conversion": ["landing", "value_prop", "objection_handling", "checkout"],
    "engagement": ["notification", "content_discovery", "interaction", "return_visit"],

    # ── Retail: Grocery ──────────────────────────────────────────────────────
    "grocery": [
        "store_entry",          # Physical or app landing — first impression
        "aisle_browse",         # Category navigation, product discovery
        "product_evaluation",   # Price check, label reading, comparison
        "basket_build",         # Adding items, substitution decisions
        "checkout_payment",     # Queue, self-checkout, delivery slot
        "post_purchase",        # Receipt review, loyalty points, reorder intent
    ],
    "grocery_loyalty": [
        "offer_awareness",      # Email/push/in-store — sees the loyalty pitch
        "value_assessment",     # Calculates: is the membership worth it?
        "signup_friction",      # Form, card, app download
        "first_redemption",     # Uses points or member price for the first time
        "habit_loop",           # Weekly shop with card — does it stick?
        "renewal_decision",     # Annual renewal or churn
    ],
    "grocery_subscription": [
        "bundle_discovery",     # Sees the subscription offer (fixed vs build-your-own)
        "value_comparison",     # Compares subscription cost vs à la carte
        "commitment_hesitation",# Worries about flexibility, waste, lock-in
        "first_delivery",       # Unboxes the first order — meets expectations?
        "routine_formation",    # Second and third delivery — habit or friction?
        "modification_or_cancel",# Wants to swap items or cancel
    ],

    # ── Ecommerce: Marketplace ─────────────────────────────────────────────
    "marketplace": [
        "search_landing",       # Search query or category page — first results
        "product_comparison",   # Compare listings, sellers, prices, reviews
        "review_deep_dive",     # Read reviews, check seller ratings, Q&A
        "add_to_cart",          # Commits intent — considers shipping, Prime, etc.
        "checkout_decision",    # Payment, shipping speed choice, promo codes
        "post_purchase",        # Delivery tracking, unbox, review or return decision
    ],
    "marketplace_returns": [
        "return_trigger",       # Wrong size, damaged, not as described
        "return_process_start", # Find return flow — label, drop-off, pickup
        "effort_assessment",    # Easy or painful? Packaging, postage, locker
        "return_completion",    # Actually ships it back
        "refund_wait",          # Waiting for refund — trust holds or erodes
        "repurchase_intent",    # Would they buy from this seller/platform again?
    ],

    # ── Ecommerce: Food Delivery ───────────────────────────────────────────
    "food_delivery": [
        "app_open_craving",     # Opens app — hungry, browsing, or habitual?
        "restaurant_browse",    # Scroll restaurants, filter, promoted listings
        "menu_selection",       # Pick items — customization, add-ons, pricing
        "cart_review",          # See total with fees, delivery charge, tip
        "order_tracking",       # Waiting — ETA updates, driver location
        "delivery_experience",  # Food arrives — quality, speed, accuracy
    ],
    "food_delivery_subscription": [
        "subscription_pitch",   # DashPass / Uber One / Grubhub+ offer
        "value_calculation",    # Will I order enough to justify the monthly fee?
        "signup_commitment",    # Enter payment — monthly or annual?
        "first_subsidized_order",# First order with free delivery — feels great
        "habit_or_guilt",       # Am I ordering too much? Or not enough to justify?
        "renewal_or_cancel",    # Monthly renewal — keep or cut?
    ],

    # ── Ecommerce: Quick Commerce ──────────────────────────────────────────
    "quick_commerce": [
        "impulse_trigger",      # Need something NOW — convenience craving
        "catalog_scan",         # Browse limited catalog — is my item here?
        "price_markup_reaction",# Notice higher prices vs grocery store
        "minimum_order_pad",    # Need to add items to hit delivery minimum
        "checkout_speed",       # One-tap checkout, saved payment, address
        "delivery_satisfaction",# 15-30 min delivery — did it meet the promise?
    ],

    # ── Ecommerce: Online Grocery ──────────────────────────────────────────
    "online_grocery": [
        "list_import",          # Start from list, past orders, or browse fresh
        "product_selection",    # Pick items — substitution preferences, organic vs regular
        "basket_review",        # Review full basket — budget check, forgotten items
        "delivery_slot_choice", # Pick time window — availability, urgency, cost
        "checkout_payment",     # Pay — tip, promo codes, membership discount
        "delivery_receipt",     # Receive order — substitutions, freshness, missing items
    ],

    # ── Retail: Fashion ──────────────────────────────────────────────────────
    "fashion": [
        "discovery",            # Ad, influencer, browse — sees the product
        "product_page",         # Photos, sizing, reviews, price
        "size_fit_doubt",       # Will this fit? Size guide, returns policy
        "add_to_cart",          # Commits intent — but hasn't paid
        "checkout_friction",    # Shipping cost reveal, payment entry, promo code hunt
        "post_purchase",        # Delivery wait, unbox, keep-or-return decision
    ],

    # ── Retail (generic) ─────────────────────────────────────────────────────
    "retail": [
        "discovery",
        "product_evaluation",
        "cart_decision",
        "checkout",
        "post_purchase",
    ],

    # ── Ecommerce (generic catch-all) ────────────────────────────────────────
    "ecommerce": [
        "discovery",
        "product_evaluation",
        "cart_decision",
        "checkout",
        "post_purchase",
    ],
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
