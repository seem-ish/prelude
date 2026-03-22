"""
Prelude — Population Generator (Slice 4)
Pure algorithmic scoring to suggest a population of personas
weighted for a given experiment. No LLM calls needed.
"""

import re
from collections import Counter
from prelude.agents.persona_library import PERSONA_LIBRARY, PERSONAS_BY_CLUSTER


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_keywords(text: str) -> set[str]:
    """Pull lowercase tokens (3+ chars) from a block of text."""
    if not text:
        return set()
    tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
    # Drop very common stop words
    stop = {
        "the", "and", "for", "that", "with", "this", "are", "from",
        "not", "but", "they", "will", "can", "has", "have", "was",
        "been", "more", "their", "about", "would", "into", "than",
        "its", "also", "could", "other", "some", "what", "when",
        "who", "how", "all", "each", "which", "does", "should",
        "our", "may", "any", "very", "just",
    }
    return set(tokens) - stop


def _persona_text_corpus(persona: dict) -> str:
    """Concatenate all text fields of a persona for keyword matching."""
    parts = [
        persona.get("description", ""),
        persona.get("short_desc", ""),
        " ".join(persona.get("motivations", [])),
        " ".join(persona.get("fears", [])),
        " ".join(persona.get("triggers", [])),
        " ".join(persona.get("abandonment_signals", [])),
        persona.get("journey_pattern", ""),
    ]
    return " ".join(parts).lower()


def _keyword_overlap(persona: dict, experiment_keywords: set[str]) -> float:
    """Return 0-1 score based on fraction of experiment keywords found in persona text."""
    if not experiment_keywords:
        return 0.0
    corpus = _persona_text_corpus(persona)
    hits = sum(1 for kw in experiment_keywords if kw in corpus)
    return min(hits / max(len(experiment_keywords), 1), 1.0)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def suggest_population(experiment: dict) -> list[dict]:
    """
    Score every persona against the experiment and return 8-12 weighted
    personas sorted by weight descending.  Weights sum to exactly 1.0.

    Returns list of {slug, name, cluster, weight, relevance_score}.
    """

    category = (experiment.get("category") or "retail").lower()

    # Build experiment keyword set from problem, target_user, product_context
    experiment_text = " ".join(filter(None, [
        experiment.get("problem"),
        experiment.get("target_user"),
        experiment.get("product_context"),
    ]))
    experiment_keywords = _extract_keywords(experiment_text)

    # --- Phase 1: score every persona ---
    raw_scores: list[tuple[dict, float]] = []

    for persona in PERSONA_LIBRARY:
        cat_score = persona.get("category_relevance", {}).get(category, 0.3)
        kw_score = _keyword_overlap(persona, experiment_keywords)
        raw = cat_score * 0.5 + kw_score * 0.3  # diversity bonus added in phase 2
        raw_scores.append((persona, raw))

    # Sort by raw score descending
    raw_scores.sort(key=lambda x: x[1], reverse=True)

    # --- Phase 2: select 8-12 with cluster diversity bonus ---
    selected: list[tuple[dict, float]] = []
    cluster_counts: Counter = Counter()
    max_per_cluster = 3  # soft cap to promote diversity

    for persona, score in raw_scores:
        cluster = persona["cluster"]
        # Diversity bonus: penalise over-represented clusters
        if cluster_counts[cluster] >= max_per_cluster:
            diversity_bonus = -0.05
        elif cluster_counts[cluster] == 0:
            diversity_bonus = 0.20  # reward first pick from a cluster
        else:
            diversity_bonus = 0.10

        final_score = score + diversity_bonus * 0.2
        selected.append((persona, final_score))
        cluster_counts[cluster] += 1

        if len(selected) >= 12:
            break

    # Ensure at least 8 (should always be true with 40 personas)
    if len(selected) < 8:
        # Shouldn't happen, but be safe
        remaining = [
            (p, s) for p, s in raw_scores
            if p["slug"] not in {s[0]["slug"] for s in selected}
        ]
        selected.extend(remaining[: 8 - len(selected)])

    # --- Phase 3: assign weights ---
    # Re-sort selected by final score descending
    selected.sort(key=lambda x: x[1], reverse=True)

    n = len(selected)
    # Linear decreasing weights, then normalise
    raw_weights = [max(n - i, 1) for i in range(n)]
    total_raw = sum(raw_weights)
    weights = [w / total_raw for w in raw_weights]

    # Enforce minimum 3%
    MIN_WEIGHT = 0.03
    for i in range(n):
        if weights[i] < MIN_WEIGHT:
            weights[i] = MIN_WEIGHT

    # Boost top to get ~25-30% and re-normalise
    weights[0] = max(weights[0], 0.25)

    # Normalise so they sum to exactly 1.0
    total = sum(weights)
    weights = [w / total for w in weights]

    # Final rounding pass — distribute rounding error into the top weight
    weights = [round(w, 4) for w in weights]
    diff = round(1.0 - sum(weights), 4)
    weights[0] = round(weights[0] + diff, 4)

    # --- Build result ---
    result = []
    for (persona, score), weight in zip(selected, weights):
        result.append({
            "slug": persona["slug"],
            "name": persona["name"],
            "cluster": persona["cluster"],
            "weight": weight,
            "relevance_score": round(score, 4),
        })

    return result
