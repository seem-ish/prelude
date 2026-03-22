"""
Prelude — Signal Extractor (Slice 5)
Extracts structured signals from simulation events for analysis.
"""

from collections import defaultdict


def _avg(values: list[float]) -> float:
    """Safe average."""
    return round(sum(values) / len(values), 3) if values else 0.0


def _adoption_by_segment(events_a: list, events_b: list, agents_by_id: dict) -> dict:
    """
    Compute adoption rate per persona segment for each variant.
    Adoption = agent ended with positive final sentiment (> 0).
    Returns: {persona_slug: {a: rate, b: rate}}
    """
    def _segment_rates(events: list) -> dict[str, dict]:
        """Returns {slug: {adopted: int, total: int}}"""
        # Group events by agent
        agent_events: dict[str, list] = defaultdict(list)
        for ev in events:
            agent_events[ev["agent_id"]].append(ev)

        segment_data: dict[str, dict] = defaultdict(lambda: {"adopted": 0, "total": 0})

        for agent_id, evts in agent_events.items():
            agent = agents_by_id.get(agent_id, {})
            blend = agent.get("persona_blend") or []
            # Get primary persona (highest influence)
            if blend:
                if isinstance(blend, list):
                    primary = max(blend, key=lambda b: b.get("influence", 0))
                    slug = primary.get("slug", "unknown")
                else:
                    slug = "unknown"
            else:
                slug = "unknown"

            # Final sentiment = average of last 2 events
            sorted_evts = sorted(evts, key=lambda e: e.get("step_index", 0))
            final_sentiments = [e["sentiment"] for e in sorted_evts[-2:]]
            final_avg = _avg(final_sentiments)

            segment_data[slug]["total"] += 1
            if final_avg > 0:
                segment_data[slug]["adopted"] += 1

        return segment_data

    rates_a = _segment_rates(events_a)
    rates_b = _segment_rates(events_b)

    all_slugs = set(list(rates_a.keys()) + list(rates_b.keys()))
    result = {}

    for slug in sorted(all_slugs):
        a_data = rates_a.get(slug, {"adopted": 0, "total": 0})
        b_data = rates_b.get(slug, {"adopted": 0, "total": 0})
        result[slug] = {
            "a": round(a_data["adopted"] / max(a_data["total"], 1), 3),
            "b": round(b_data["adopted"] / max(b_data["total"], 1), 3),
        }

    return result


def _friction_heatmap(events_a: list, events_b: list) -> list[dict]:
    """
    Compute friction at each journey step.
    Friction = proportion of negative sentiment events at that step.
    Returns: [{step, a_friction, b_friction}]
    """
    def _step_friction(events: list) -> dict[str, float]:
        step_neg: dict[str, int] = defaultdict(int)
        step_total: dict[str, int] = defaultdict(int)
        for ev in events:
            step = ev.get("step", "unknown")
            step_total[step] += 1
            if ev["sentiment"] < -0.2:
                step_neg[step] += 1
        return {
            step: round(step_neg.get(step, 0) / max(count, 1), 3)
            for step, count in step_total.items()
        }

    friction_a = _step_friction(events_a)
    friction_b = _step_friction(events_b)
    all_steps = list(dict.fromkeys(
        [e.get("step", "unknown") for e in events_a]
        + [e.get("step", "unknown") for e in events_b]
    ))

    return [
        {
            "step": step,
            "a_friction": friction_a.get(step, 0.0),
            "b_friction": friction_b.get(step, 0.0),
        }
        for step in all_steps
    ]


def _sentiment_arc(events_a: list, events_b: list) -> dict:
    """
    Compute average sentiment per journey step for each variant.
    Returns: {a: [step_scores], b: [step_scores]}
    """
    def _step_sentiments(events: list) -> list[float]:
        step_vals: dict[int, list[float]] = defaultdict(list)
        for ev in events:
            idx = ev.get("step_index", 0)
            step_vals[idx].append(ev["sentiment"])
        if not step_vals:
            return []
        max_idx = max(step_vals.keys())
        return [_avg(step_vals.get(i, [])) for i in range(max_idx + 1)]

    return {
        "a": _step_sentiments(events_a),
        "b": _step_sentiments(events_b),
    }


def _top_quotes(events_a: list, events_b: list) -> list[dict]:
    """
    Pick the most interesting quotes: extreme sentiments from both variants.
    Returns: [{agent, content, sentiment, variant}]
    """
    quotes = []

    for variant_label, events in [("a", events_a), ("b", events_b)]:
        sorted_events = sorted(events, key=lambda e: abs(e["sentiment"]), reverse=True)
        seen_content = set()
        for ev in sorted_events:
            if ev["content"] not in seen_content:
                seen_content.add(ev["content"])
                quotes.append({
                    "agent": ev.get("agent_name", ""),
                    "content": ev["content"],
                    "sentiment": ev["sentiment"],
                    "variant": variant_label,
                })
            if len(quotes) >= 10:
                break

    # Sort by absolute sentiment, take top 10
    quotes.sort(key=lambda q: abs(q["sentiment"]), reverse=True)
    return quotes[:10]


def _behavioral_patterns(events_a: list, events_b: list) -> list[str]:
    """
    Identify high-level behavioral patterns from the events.
    Returns: list of human-readable pattern descriptions.
    """
    patterns = []

    # Compare overall sentiment
    avg_a = _avg([e["sentiment"] for e in events_a]) if events_a else 0
    avg_b = _avg([e["sentiment"] for e in events_b]) if events_b else 0

    if avg_b > avg_a + 0.1:
        patterns.append(
            f"Variant B shows higher overall sentiment ({avg_b:.2f}) vs A ({avg_a:.2f}), "
            "suggesting stronger positive reception."
        )
    elif avg_a > avg_b + 0.1:
        patterns.append(
            f"Variant A shows higher overall sentiment ({avg_a:.2f}) vs B ({avg_b:.2f}), "
            "suggesting the incumbent approach resonates more."
        )
    else:
        patterns.append(
            f"Both variants show similar overall sentiment (A: {avg_a:.2f}, B: {avg_b:.2f}). "
            "Differentiation may depend on specific segments."
        )

    # Check abandonment rates
    abandon_a = sum(1 for e in events_a if "abandon" in e.get("content", "").lower())
    abandon_b = sum(1 for e in events_b if "abandon" in e.get("content", "").lower())
    if abandon_a > abandon_b:
        patterns.append(
            f"Variant A has more abandonment signals ({abandon_a} vs {abandon_b}), "
            "indicating higher friction in the current approach."
        )
    elif abandon_b > abandon_a:
        patterns.append(
            f"Variant B has more abandonment signals ({abandon_b} vs {abandon_a}), "
            "suggesting the new approach may introduce unexpected friction."
        )

    # Check emotional engagement
    emotion_a = [e for e in events_a if e.get("event_type") == "emotion"]
    emotion_b = [e for e in events_b if e.get("event_type") == "emotion"]
    if emotion_a and emotion_b:
        emo_avg_a = _avg([e["sentiment"] for e in emotion_a])
        emo_avg_b = _avg([e["sentiment"] for e in emotion_b])
        if abs(emo_avg_a - emo_avg_b) > 0.15:
            stronger = "B" if emo_avg_b > emo_avg_a else "A"
            patterns.append(
                f"Variant {stronger} elicits stronger positive emotional responses, "
                "which typically correlates with higher long-term retention."
            )

    # Check decision confidence
    decision_a = [e for e in events_a if e.get("event_type") == "decision"]
    decision_b = [e for e in events_b if e.get("event_type") == "decision"]
    if decision_a and decision_b:
        dec_avg_a = _avg([e["sentiment"] for e in decision_a])
        dec_avg_b = _avg([e["sentiment"] for e in decision_b])
        if dec_avg_b > dec_avg_a + 0.1:
            patterns.append(
                "Agents show stronger purchase/commitment intent with Variant B."
            )
        elif dec_avg_a > dec_avg_b + 0.1:
            patterns.append(
                "Agents show stronger purchase/commitment intent with Variant A."
            )

    return patterns


def extract_signals(events_a: list, events_b: list, experiment: dict) -> dict:
    """
    Analyze events from both variants to produce structured signals.

    Args:
        events_a: list of event dicts from variant A
        events_b: list of event dicts from variant B
        experiment: full experiment row from DB

    Returns:
        {
            adoption_by_segment: {persona_slug: {a: rate, b: rate}},
            friction_heatmap: [{step, a_friction, b_friction}],
            sentiment_arc: {a: [step_scores], b: [step_scores]},
            top_quotes: [{agent, content, sentiment, variant}],
            behavioral_patterns: [str],
        }
    """
    # Build agents lookup from events
    agents_by_id: dict[str, dict] = {}
    all_events = events_a + events_b
    for ev in all_events:
        aid = ev.get("agent_id")
        if aid and aid not in agents_by_id:
            # Reconstruct minimal agent info from event data
            # In a real system we'd query the DB, but events carry agent metadata
            agents_by_id[aid] = {
                "id": aid,
                "name": ev.get("agent_name", ""),
                "persona_blend": ev.get("persona_blend", []),
                "traits": ev.get("traits", {}),
            }

    # If events carry persona info from the orchestrator seed, use it
    # Otherwise try to load from DB
    if not any(agents_by_id[a].get("persona_blend") for a in agents_by_id):
        try:
            from prelude.db import query as db_query
            agent_ids = list(agents_by_id.keys())
            if agent_ids:
                placeholders = ", ".join(["%s"] * len(agent_ids))
                rows = db_query(
                    f"SELECT * FROM agents WHERE id IN ({placeholders})",
                    tuple(agent_ids),
                )
                for row in rows:
                    aid = str(row["id"])
                    agents_by_id[aid] = dict(row)
        except Exception:
            pass  # graceful degradation — signals will use "unknown" segments

    return {
        "adoption_by_segment": _adoption_by_segment(events_a, events_b, agents_by_id),
        "friction_heatmap": _friction_heatmap(events_a, events_b),
        "sentiment_arc": _sentiment_arc(events_a, events_b),
        "top_quotes": _top_quotes(events_a, events_b),
        "behavioral_patterns": _behavioral_patterns(events_a, events_b),
    }
