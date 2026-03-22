"""
Prelude — Calibration API (Slice 7)
POST /api/prelude/experiments/<exp_id>/calibration  — log real outcome
GET  /api/prelude/experiments/<exp_id>/calibration   — get calibration data
GET  /api/prelude/team/calibration                   — aggregate team stats
"""

from flask import Blueprint, request, jsonify
from prelude.db import query, execute_returning

calibration_bp = Blueprint("calibration", __name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _serialize(row: dict) -> dict:
    """Make a DB row JSON-safe."""
    out = dict(row)
    for k, v in out.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "__str__") and type(v).__name__ == "UUID":
            out[k] = str(v)
    return out


# ─── POST /calibration ───────────────────────────────────────────────────────

@calibration_bp.route("/calibration", methods=["POST"])
def log_calibration(exp_id):
    """
    Log the real-world outcome for an experiment so it can be
    compared against the prediction.

    Body:
        actual_winner       — "a" or "b"
        direction_correct   — bool
        segment_correct     — bool
        friction_correct    — bool
        notes               — optional free-text
    """
    body = request.get_json(force=True) or {}

    actual_winner = body.get("actual_winner", "").strip().lower()
    if actual_winner not in ("a", "b"):
        return jsonify({"error": "actual_winner must be 'a' or 'b'"}), 400

    direction_correct = body.get("direction_correct")
    segment_correct = body.get("segment_correct")
    friction_correct = body.get("friction_correct")

    if not isinstance(direction_correct, bool):
        return jsonify({"error": "direction_correct must be a boolean"}), 400
    if not isinstance(segment_correct, bool):
        return jsonify({"error": "segment_correct must be a boolean"}), 400
    if not isinstance(friction_correct, bool):
        return jsonify({"error": "friction_correct must be a boolean"}), 400

    notes = body.get("notes", "")

    # Look up the predicted winner from the predictions table
    pred_rows = query(
        "SELECT winner FROM predictions WHERE experiment_id = %s",
        (str(exp_id),),
    )
    predicted_winner = pred_rows[0]["winner"] if pred_rows else None

    row = execute_returning(
        """
        INSERT INTO calibration_log
            (experiment_id, predicted_winner, actual_winner,
             direction_correct, segment_correct, friction_correct, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (experiment_id) DO UPDATE SET
            predicted_winner  = EXCLUDED.predicted_winner,
            actual_winner     = EXCLUDED.actual_winner,
            direction_correct = EXCLUDED.direction_correct,
            segment_correct   = EXCLUDED.segment_correct,
            friction_correct  = EXCLUDED.friction_correct,
            notes             = EXCLUDED.notes,
            logged_at         = NOW()
        RETURNING *
        """,
        (
            str(exp_id),
            predicted_winner,
            actual_winner,
            direction_correct,
            segment_correct,
            friction_correct,
            notes,
        ),
    )
    return jsonify(_serialize(row)), 201


# ─── GET /calibration ────────────────────────────────────────────────────────

@calibration_bp.route("/calibration", methods=["GET"])
def get_calibration(exp_id):
    """
    Return the calibration entry for a specific experiment.
    """
    rows = query(
        "SELECT * FROM calibration_log WHERE experiment_id = %s",
        (str(exp_id),),
    )
    if not rows:
        return jsonify({"error": "No calibration data for this experiment"}), 404

    return jsonify(_serialize(rows[0]))


# ─── Team-level calibration blueprint ────────────────────────────────────────

team_calibration_bp = Blueprint("team_calibration", __name__)


@team_calibration_bp.route("/calibration", methods=["GET"])
def team_calibration_stats():
    """
    Aggregate calibration accuracy across all experiments for the team.
    Returns:
        total_logged        — number of calibrated experiments
        direction_accuracy  — fraction of correct direction calls
        segment_accuracy    — fraction of correct segment calls
        friction_accuracy   — fraction of correct friction calls
        strongest_cluster   — which dimension has highest accuracy
        weakest_area        — which dimension has lowest accuracy
    """
    rows = query("SELECT * FROM calibration_log ORDER BY logged_at DESC")

    if not rows:
        return jsonify({
            "total_logged": 0,
            "direction_accuracy": None,
            "segment_accuracy": None,
            "friction_accuracy": None,
            "strongest_cluster": None,
            "weakest_area": None,
        })

    total = len(rows)
    direction_hits = sum(1 for r in rows if r.get("direction_correct"))
    segment_hits = sum(1 for r in rows if r.get("segment_correct"))
    friction_hits = sum(1 for r in rows if r.get("friction_correct"))

    direction_acc = round(direction_hits / total, 3)
    segment_acc = round(segment_hits / total, 3)
    friction_acc = round(friction_hits / total, 3)

    scores = {
        "direction": direction_acc,
        "segment": segment_acc,
        "friction": friction_acc,
    }
    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)

    return jsonify({
        "total_logged": total,
        "direction_accuracy": direction_acc,
        "segment_accuracy": segment_acc,
        "friction_accuracy": friction_acc,
        "strongest_cluster": strongest,
        "weakest_area": weakest,
    })
