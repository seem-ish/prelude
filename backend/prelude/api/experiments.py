"""
Prelude — Experiments API
GET  /api/prelude/experiments          list all
POST /api/prelude/experiments          create
GET  /api/prelude/experiments/:id      get one
PATCH /api/prelude/experiments/:id     update
"""

import json
from flask import Blueprint, request, jsonify
from prelude.db import query, execute_returning, execute

experiments_bp = Blueprint("experiments", __name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _serialize(row):
    """Make a DB row JSON-safe (UUID → str, datetime → iso)."""
    out = dict(row)
    for k, v in out.items():
        if hasattr(v, 'isoformat'):
            out[k] = v.isoformat()
        elif hasattr(v, '__str__') and type(v).__name__ == 'UUID':
            out[k] = str(v)
    return out


def _with_winner(exp):
    """Attach winner + confidence from predictions table if available."""
    rows = query(
        "SELECT winner, confidence FROM predictions WHERE experiment_id = %s",
        (str(exp['id']),)
    )
    if rows:
        exp['winner'] = rows[0]['winner']
        exp['confidence'] = rows[0]['confidence']
    else:
        exp['winner'] = None
        exp['confidence'] = None
    return exp


# ─── Routes ───────────────────────────────────────────────────────────────────

@experiments_bp.route("", methods=["GET"])
def list_experiments():
    rows = query(
        "SELECT * FROM experiments ORDER BY created_at DESC"
    )
    experiments = [_with_winner(_serialize(r)) for r in rows]
    return jsonify(experiments)


@experiments_bp.route("", methods=["POST"])
def create_experiment():
    body = request.get_json(force=True) or {}

    title = body.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    # Resolve or create a default team
    teams = query("SELECT id FROM teams ORDER BY created_at LIMIT 1")
    if not teams:
        team = execute_returning(
            "INSERT INTO teams (name) VALUES (%s) RETURNING id", ("Default Team",)
        )
        team_id = team["id"]
    else:
        team_id = teams[0]["id"]

    row = execute_returning(
        """
        INSERT INTO experiments
          (team_id, title, problem, variant_a, variant_b,
           target_user, success_metric, product_context, category, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            str(team_id),
            title,
            body.get("problem"),
            body.get("variant_a"),
            body.get("variant_b"),
            body.get("target_user"),
            body.get("success_metric"),
            body.get("product_context"),
            body.get("category"),
            body.get("status", "draft"),
        )
    )
    result = _serialize(row)
    result['winner'] = None
    result['confidence'] = None
    return jsonify(result), 201


@experiments_bp.route("/<exp_id>", methods=["GET"])
def get_experiment(exp_id):
    rows = query("SELECT * FROM experiments WHERE id = %s", (exp_id,))
    if not rows:
        return jsonify({"error": "not found"}), 404
    return jsonify(_with_winner(_serialize(rows[0])))


@experiments_bp.route("/<exp_id>", methods=["PATCH"])
def update_experiment(exp_id):
    body = request.get_json(force=True) or {}

    allowed = {
        "title", "problem", "variant_a", "variant_b",
        "target_user", "success_metric", "product_context",
        "category", "status"
    }
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return jsonify({"error": "no valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [exp_id]

    rows = query(
        f"UPDATE experiments SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING *",
        values
    )
    if not rows:
        return jsonify({"error": "not found"}), 404
    return jsonify(_with_winner(_serialize(rows[0])))
