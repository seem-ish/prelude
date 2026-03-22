"""
Prelude — Prediction API (Slice 6)
POST /api/prelude/experiments/<exp_id>/predict   — trigger prediction generation
GET  /api/prelude/experiments/<exp_id>/prediction — retrieve completed prediction
"""

import json
from flask import Blueprint, jsonify
from prelude.db import query
from prelude.prediction.prediction_engine import generate_prediction

prediction_bp = Blueprint("prediction", __name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _serialize(row: dict) -> dict:
    """Make a DB row JSON-safe."""
    out = dict(row)
    for k, v in out.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "__str__") and type(v).__name__ == "UUID":
            out[k] = str(v)
    for field in ("segment_story", "watch_items"):
        if isinstance(out.get(field), str):
            out[field] = json.loads(out[field])
    return out


# ─── POST /predict ────────────────────────────────────────────────────────────

@prediction_bp.route("/predict", methods=["POST"])
def trigger_prediction(exp_id):
    """
    Generate (or regenerate) a prediction for this experiment.
    The engine loads experiment data + run signals from the DB,
    builds the prediction, and upserts it into the predictions table.
    """
    try:
        prediction = generate_prediction(exp_id)
        return jsonify(prediction), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Prediction generation failed: {e}"}), 500


# ─── GET /prediction ──────────────────────────────────────────────────────────

@prediction_bp.route("/prediction", methods=["GET"])
def get_prediction(exp_id):
    """
    Retrieve the stored prediction for an experiment.
    Returns 404 if no prediction has been generated yet.
    """
    rows = query(
        "SELECT * FROM predictions WHERE experiment_id = %s",
        (str(exp_id),),
    )
    if not rows:
        return jsonify({"error": "No prediction found for this experiment"}), 404

    return jsonify(_serialize(rows[0]))
