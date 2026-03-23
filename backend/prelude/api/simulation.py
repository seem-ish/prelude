"""
Prelude — Simulation API (Slice 5)
Endpoints for triggering and querying simulation runs.
"""

import json
from flask import Blueprint, request, jsonify
from prelude.db import query, execute_returning
from prelude.simulation.orchestrator import run_ab_simulation

simulation_bp = Blueprint("simulation", __name__)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _serialize(row: dict) -> dict:
    """Make a DB row JSON-safe."""
    out = dict(row)
    for k, v in out.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "__str__") and type(v).__name__ == "UUID":
            out[k] = str(v)
    return out


# ─── POST /simulate ─────────────────────────────────────────────────────────

@simulation_bp.route("/simulate", methods=["POST"])
def trigger_simulation(exp_id):
    """
    Trigger an A/B simulation run for the experiment.
    Synchronous for now — returns when both variants are complete.
    """
    # Verify experiment exists
    rows = query("SELECT id FROM experiments WHERE id = %s", (exp_id,))
    if not rows:
        return jsonify({"error": "experiment not found"}), 404

    try:
        results = run_ab_simulation(exp_id)
        return jsonify(results)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Simulation failed: {str(exc)}"}), 500


# ─── GET /runs ───────────────────────────────────────────────────────────────

@simulation_bp.route("/runs", methods=["GET"])
def get_runs(exp_id):
    """
    Get all simulation runs and their signals for this experiment.
    """
    runs = query(
        """
        SELECT sr.*,
               rs.adoption_by_segment,
               rs.friction_heatmap,
               rs.sentiment_arc,
               rs.top_quotes,
               rs.behavioral_patterns,
               rs.voc_output
        FROM simulation_runs sr
        LEFT JOIN run_signals rs ON rs.run_id = sr.id
        WHERE sr.experiment_id = %s
        ORDER BY sr.started_at DESC
        """,
        (exp_id,),
    )

    if not runs:
        return jsonify({"runs": [], "signals": None})

    serialized_runs = [_serialize(row) for row in runs]

    # Extract the latest signals (from the most recent run)
    latest = runs[0]
    signals = None
    if latest.get("adoption_by_segment") is not None:
        signals = {
            "adoption_by_segment": latest["adoption_by_segment"],
            "friction_heatmap": latest["friction_heatmap"],
            "sentiment_arc": latest["sentiment_arc"],
            "top_quotes": latest["top_quotes"],
            "behavioral_patterns": latest["behavioral_patterns"],
        }

    # Include VoC if available (v1 mode)
    voc = latest.get("voc_output") if latest else None

    return jsonify({
        "runs": serialized_runs,
        "signals": signals,
        "voc": voc,
    })


# ─── GET /events ─────────────────────────────────────────────────────────────

@simulation_bp.route("/events", methods=["GET"])
def get_events(exp_id):
    """
    Get all agent events for the experiment across all runs.
    Optional query params: variant, step, event_type
    """
    variant = request.args.get("variant")
    step = request.args.get("step")
    event_type = request.args.get("event_type")

    base_sql = """
        SELECT ae.*, sr.variant, a.name AS agent_name,
               a.persona_blend, a.traits
        FROM agent_events ae
        JOIN simulation_runs sr ON sr.id = ae.run_id
        JOIN agents a ON a.id = ae.agent_id
        WHERE sr.experiment_id = %s
    """
    params = [exp_id]

    if variant:
        base_sql += " AND sr.variant = %s"
        params.append(variant)
    if step:
        base_sql += " AND ae.journey_step = %s"
        params.append(step)
    if event_type:
        base_sql += " AND ae.event_type = %s"
        params.append(event_type)

    base_sql += " ORDER BY ae.created_at"

    events = query(base_sql, tuple(params))
    serialized = [_serialize(row) for row in events]

    return jsonify({
        "events": serialized,
        "total": len(serialized),
    })
