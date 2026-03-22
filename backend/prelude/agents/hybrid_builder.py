"""
Prelude — Hybrid Agent Builder (Slice 4)
Build N hybrid agents from weighted persona selection.
Each agent blends a primary, secondary, and optional tertiary persona.
No LLM calls — backstories are template-generated.
"""

import random
from prelude.agents.persona_library import PERSONAS_BY_SLUG, PERSONAS_BY_CLUSTER

# ---------------------------------------------------------------------------
# Culturally diverse first-name pool (120+)
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    # English / Anglo
    "James", "Olivia", "Liam", "Emma", "Noah", "Ava", "Sophia", "Mason",
    "Isabella", "Ethan", "Mia", "Lucas", "Charlotte", "Harper", "Aiden",
    "Ella", "Jackson", "Amelia", "Sebastian", "Luna",
    # Hispanic / Latin
    "Mateo", "Valentina", "Santiago", "Camila", "Diego", "Mariana", "Andres",
    "Lucia", "Rafael", "Elena", "Carlos", "Gabriela", "Alejandro", "Sofia",
    "Joaquin", "Isabel",
    # East Asian
    "Wei", "Yuki", "Hiro", "Mei", "Jun", "Sakura", "Kenji", "Aiko",
    "Sora", "Haruki", "Rin", "Min-jun", "Ji-yeon", "Tao", "Linh", "Minh",
    # South Asian
    "Arjun", "Priya", "Rohan", "Ananya", "Vikram", "Devi", "Kiran", "Neha",
    "Aarav", "Saanvi", "Ravi", "Meera", "Ishaan", "Aisha", "Nikhil", "Pooja",
    # African
    "Amara", "Kofi", "Zuri", "Kwame", "Nia", "Jelani", "Imani", "Tendai",
    "Chioma", "Emeka", "Fatima", "Ousmane", "Adaeze", "Sekou", "Amina", "Tariq",
    # Middle Eastern
    "Omar", "Layla", "Yusuf", "Nadia", "Hassan", "Salma", "Kareem", "Rania",
    "Zayn", "Leila", "Ibrahim", "Yasmin", "Samir", "Dina", "Khalid", "Hana",
    # Eastern European
    "Dmitri", "Katya", "Mikhail", "Anastasia", "Pavel", "Irina", "Nikola",
    "Marta", "Stefan", "Ivana", "Boris", "Tatiana", "Oleg", "Petra",
    # Western European
    "Luca", "Elise", "Henrik", "Ingrid", "Matteo", "Celine", "Finn",
    "Astrid", "Hugo", "Freya", "Leon", "Amelie", "Felix", "Clara",
    # Indigenous / Pacific
    "Aroha", "Tane", "Marisol", "Kai", "Leilani", "Manu", "Moana", "Tui",
]

# ---------------------------------------------------------------------------
# Backstory templates — filled from persona data
# ---------------------------------------------------------------------------
_BACKSTORY_TEMPLATES = [
    (
        "{name} is someone who {journey_pattern_lower}. "
        "Driven by a desire to {motivation}, they tend to worry about {fear}."
    ),
    (
        "{name} approaches new products by {journey_pattern_lower}. "
        "Their biggest concern is {fear}, but the right {trigger} can win them over."
    ),
    (
        "For {name}, {motivation} is what matters most. "
        "They typically {journey_pattern_lower}, and lose interest when {abandonment}."
    ),
    (
        "{name} is motivated by {motivation}. "
        "They follow a pattern of {journey_pattern_lower}, but {fear} can stop them cold."
    ),
    (
        "When evaluating something new, {name} will {journey_pattern_lower}. "
        "They respond to {trigger}, yet remain wary of {fear}."
    ),
]


def _pick_random(lst: list) -> str:
    """Return a random element from a list, or a fallback."""
    if not lst:
        return "making good choices"
    return random.choice(lst)


def _generate_backstory(name: str, persona_blend: list[dict]) -> str:
    """Build a 2-sentence backstory from persona data using templates."""
    primary = PERSONAS_BY_SLUG.get(persona_blend[0]["slug"], {})
    template = random.choice(_BACKSTORY_TEMPLATES)

    journey = primary.get("journey_pattern", "exploring options carefully")
    # lowercase the journey pattern for natural sentence flow
    journey_lower = journey[0].lower() + journey[1:] if journey else "exploring carefully"

    backstory = template.format(
        name=name,
        journey_pattern_lower=journey_lower,
        motivation=_pick_random(primary.get("motivations", [])).lower(),
        fear=_pick_random(primary.get("fears", [])).lower(),
        trigger=_pick_random(primary.get("triggers", [])).lower(),
        abandonment=_pick_random(primary.get("abandonment_signals", [])).lower(),
    )
    return backstory


# ---------------------------------------------------------------------------
# Core builder
# ---------------------------------------------------------------------------

def _weighted_choice(persona_weights: dict) -> str:
    """Select a persona slug by weighted random."""
    slugs = list(persona_weights.keys())
    weights = [persona_weights[s] for s in slugs]
    return random.choices(slugs, weights=weights, k=1)[0]


def _pick_secondary(primary_slug: str, persona_weights: dict) -> str | None:
    """Pick a secondary persona from a different cluster than primary."""
    primary = PERSONAS_BY_SLUG.get(primary_slug)
    if not primary:
        return None
    primary_cluster = primary["cluster"]

    # Candidates: personas in persona_weights that belong to a different cluster
    candidates = {
        slug: w for slug, w in persona_weights.items()
        if slug != primary_slug
        and PERSONAS_BY_SLUG.get(slug, {}).get("cluster") != primary_cluster
    }
    if not candidates:
        # Fallback: any different persona
        candidates = {
            slug: w for slug, w in persona_weights.items()
            if slug != primary_slug
        }
    if not candidates:
        return None

    slugs = list(candidates.keys())
    weights = [candidates[s] for s in slugs]
    return random.choices(slugs, weights=weights, k=1)[0]


def _pick_tertiary(
    primary_slug: str, secondary_slug: str | None, persona_weights: dict
) -> str | None:
    """Optionally pick a tertiary persona (50% chance)."""
    if random.random() > 0.5:
        return None

    exclude = {primary_slug}
    if secondary_slug:
        exclude.add(secondary_slug)

    candidates = {
        slug: w for slug, w in persona_weights.items()
        if slug not in exclude
    }
    if not candidates:
        return None

    slugs = list(candidates.keys())
    weights = [candidates[s] for s in slugs]
    return random.choices(slugs, weights=weights, k=1)[0]


def _blend_traits(components: list[tuple[str, float]]) -> dict:
    """
    Weighted-average the numeric traits of blended personas.
    components: [(slug, influence_weight), ...]
    """
    trait_keys = [
        "price_sensitivity", "trust_baseline", "decision_speed",
        "tech_comfort", "frustration_threshold", "research_depth",
        "social_influence", "risk_tolerance",
    ]
    blended: dict[str, float] = {k: 0.0 for k in trait_keys}

    total_weight = sum(w for _, w in components)
    for slug, weight in components:
        persona = PERSONAS_BY_SLUG.get(slug, {})
        traits = persona.get("traits", {})
        for key in trait_keys:
            blended[key] += traits.get(key, 0.5) * (weight / total_weight)

    # Add small per-agent noise (±0.05) and clamp to [0, 1]
    for key in trait_keys:
        noise = random.uniform(-0.05, 0.05)
        blended[key] = round(max(0.0, min(1.0, blended[key] + noise)), 3)

    return blended


def build_agents(persona_weights: dict, count: int = 200) -> list[dict]:
    """
    Build *count* hybrid agents from the given persona weight distribution.

    persona_weights: {slug: weight_float, ...}
    Returns list of agent dicts ready for DB insert:
        {name, persona_blend, traits, backstory}

    Each agent has:
    - primary persona (65% influence), secondary (25%), optional tertiary (10%)
    - Primary selected by weighted random from persona_weights
    - Secondary from a different cluster than primary
    - Traits = weighted average of component persona traits + small noise
    - Name from culturally diverse pool
    - Backstory = template-generated from persona data
    """
    if not persona_weights:
        return []

    # Shuffle name pool, cycling if count > len
    name_pool = list(FIRST_NAMES)
    random.shuffle(name_pool)

    agents: list[dict] = []
    used_names: set[str] = set()

    for i in range(count):
        # Pick name — cycle through pool with numeric suffix if needed
        base_name = name_pool[i % len(name_pool)]
        name = base_name
        cycle = i // len(name_pool)
        if cycle > 0:
            name = f"{base_name} {cycle + 1}"

        # Pick personas
        primary_slug = _weighted_choice(persona_weights)
        secondary_slug = _pick_secondary(primary_slug, persona_weights)
        tertiary_slug = _pick_tertiary(primary_slug, secondary_slug, persona_weights)

        # Build blend list with influence weights
        components: list[tuple[str, float]] = [(primary_slug, 0.65)]
        persona_blend = [{"slug": primary_slug, "influence": 0.65}]

        if secondary_slug:
            if tertiary_slug:
                components.append((secondary_slug, 0.25))
                components.append((tertiary_slug, 0.10))
                persona_blend.append({"slug": secondary_slug, "influence": 0.25})
                persona_blend.append({"slug": tertiary_slug, "influence": 0.10})
            else:
                components.append((secondary_slug, 0.35))
                persona_blend.append({"slug": secondary_slug, "influence": 0.35})

        # Blend traits
        traits = _blend_traits(components)

        # Generate backstory
        backstory = _generate_backstory(name, persona_blend)

        agents.append({
            "name": name,
            "persona_blend": persona_blend,
            "traits": traits,
            "backstory": backstory,
        })

    return agents
