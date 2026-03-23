"""
Prelude — Voice of Customer Formatter (v1)
Structures raw agent VoC quotes into segment-level readout.
"""

from collections import defaultdict


def format_voc(events_a: list, events_b: list, agents_by_id: dict) -> dict:
    """
    Organize VoC quotes by segment × step × variant.

    Returns:
        {
            "by_segment": {
                "<cluster>": {
                    "name": "Budget Hunters",
                    "quotes_a": [{step, agent, quote, sentiment}],
                    "quotes_b": [{step, agent, quote, sentiment}],
                    "avg_sentiment_a": float,
                    "avg_sentiment_b": float,
                    "preference": "a" | "b" | "split",
                }
            },
            "by_step": {
                "<step>": {
                    "quotes_a": [...],
                    "quotes_b": [...],
                    "a_avg": float,
                    "b_avg": float,
                }
            },
            "highlight_quotes": [top 8 most extreme/interesting quotes],
            "summary": {
                "total_quotes_a": int,
                "total_quotes_b": int,
                "segments_preferring_a": int,
                "segments_preferring_b": int,
            }
        }
    """

    def _agent_cluster(agent_id: str) -> str:
        agent = agents_by_id.get(agent_id, {})
        blend = agent.get("persona_blend") or []
        if isinstance(blend, list) and blend:
            primary = max(blend, key=lambda b: b.get("influence", 0))
            return primary.get("cluster", "unknown")
        return "unknown"

    def _agent_name(agent_id: str) -> str:
        agent = agents_by_id.get(agent_id, {})
        return agent.get("name", "Agent")

    def _process_events(events: list) -> list[dict]:
        """Extract quote records from events."""
        quotes = []
        for ev in events:
            content = ev.get("content", "")
            if not content:
                continue
            quotes.append({
                "step": ev.get("step", "unknown"),
                "step_index": ev.get("step_index", 0),
                "agent_id": ev.get("agent_id", ""),
                "agent": ev.get("agent_name", _agent_name(ev.get("agent_id", ""))),
                "cluster": _agent_cluster(ev.get("agent_id", "")),
                "quote": content,
                "sentiment": ev.get("sentiment", 0.0),
                "event_type": ev.get("event_type", "reaction"),
            })
        return quotes

    def _avg(values: list[float]) -> float:
        return round(sum(values) / len(values), 3) if values else 0.0

    quotes_a = _process_events(events_a)
    quotes_b = _process_events(events_b)

    # ── By segment ───────────────────────────────────────────────────────
    seg_a = defaultdict(list)
    seg_b = defaultdict(list)
    for q in quotes_a:
        seg_a[q["cluster"]].append(q)
    for q in quotes_b:
        seg_b[q["cluster"]].append(q)

    all_clusters = sorted(set(list(seg_a.keys()) + list(seg_b.keys())))
    by_segment = {}
    seg_pref_a = 0
    seg_pref_b = 0

    for cluster in all_clusters:
        a_quotes = seg_a.get(cluster, [])
        b_quotes = seg_b.get(cluster, [])
        avg_a = _avg([q["sentiment"] for q in a_quotes])
        avg_b = _avg([q["sentiment"] for q in b_quotes])

        if avg_b > avg_a + 0.05:
            pref = "b"
            seg_pref_b += 1
        elif avg_a > avg_b + 0.05:
            pref = "a"
            seg_pref_a += 1
        else:
            pref = "split"

        # Keep top 3 most expressive quotes per variant per segment
        a_top = sorted(a_quotes, key=lambda q: abs(q["sentiment"]), reverse=True)[:3]
        b_top = sorted(b_quotes, key=lambda q: abs(q["sentiment"]), reverse=True)[:3]

        by_segment[cluster] = {
            "name": cluster.replace("_", " ").title(),
            "quotes_a": a_top,
            "quotes_b": b_top,
            "avg_sentiment_a": avg_a,
            "avg_sentiment_b": avg_b,
            "preference": pref,
        }

    # ── By step ──────────────────────────────────────────────────────────
    step_a = defaultdict(list)
    step_b = defaultdict(list)
    for q in quotes_a:
        step_a[q["step"]].append(q)
    for q in quotes_b:
        step_b[q["step"]].append(q)

    all_steps_set = list(dict.fromkeys(
        [q["step"] for q in quotes_a] + [q["step"] for q in quotes_b]
    ))
    by_step = {}
    for step in all_steps_set:
        a_qs = step_a.get(step, [])
        b_qs = step_b.get(step, [])
        by_step[step] = {
            "quotes_a": sorted(a_qs, key=lambda q: abs(q["sentiment"]), reverse=True)[:3],
            "quotes_b": sorted(b_qs, key=lambda q: abs(q["sentiment"]), reverse=True)[:3],
            "a_avg": _avg([q["sentiment"] for q in a_qs]),
            "b_avg": _avg([q["sentiment"] for q in b_qs]),
        }

    # ── Highlight quotes (top 8 most extreme across both variants) ───────
    all_quotes = (
        [{"variant": "a", **q} for q in quotes_a]
        + [{"variant": "b", **q} for q in quotes_b]
    )
    all_quotes.sort(key=lambda q: abs(q["sentiment"]), reverse=True)

    # Deduplicate by content
    seen = set()
    highlights = []
    for q in all_quotes:
        if q["quote"] not in seen:
            seen.add(q["quote"])
            highlights.append(q)
        if len(highlights) >= 8:
            break

    return {
        "by_segment": by_segment,
        "by_step": by_step,
        "highlight_quotes": highlights,
        "summary": {
            "total_quotes_a": len(quotes_a),
            "total_quotes_b": len(quotes_b),
            "segments_preferring_a": seg_pref_a,
            "segments_preferring_b": seg_pref_b,
        },
    }
