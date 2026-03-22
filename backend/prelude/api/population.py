"""
Prelude — Population API (Slice 4)
Endpoints for generating, building, and viewing experiment populations.
"""

import json
from flask import Blueprint, request, jsonify
from prelude.db import query, execute_returning, execute
from prelude.agents.population_generator import suggest_population
from prelude.agents.hybrid_builder import build_agents

population_bp = Blueprint("population", __name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_experiment(exp_id: str) -> dict | None:
    rows = query("SELECT * FROM experiments WHERE id = %s", (exp_id,))
    return dict(rows[0]) if rows else None


def _serialize(row: dict) -> dict:
    """Make a DB row JSON-safe."""
    out = dict(row)
    for k, v in out.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "__str__") and type(v).__name__ == "UUID":
            out[k] = str(v)
    return out


# ─── POST /generate ──────────────────────────────────────────────────────────

@population_bp.route("/generate", methods=["POST"])
def generate_population(exp_id):
    """
    Use the experiment brief to algorithmically suggest a weighted
    persona population.  Body can be empty — data comes from the DB.
    """
    experiment = _get_experiment(exp_id)
    if not experiment:
        return jsonify({"error": "experiment not found"}), 404

    personas = suggest_population(experiment)
    return jsonify({"personas": personas})


# ─── POST /build ──────────────────────────────────────────────────────────────

@population_bp.route("/build", methods=["POST"])
def build_population(exp_id):
    """
    Create hybrid agents in the DB for this experiment.
    Body: {persona_weights: {slug: weight, ...}, agent_count: 200}
    """
    experiment = _get_experiment(exp_id)
    if not experiment:
        return jsonify({"error": "experiment not found"}), 404

    body = request.get_json(force=True) or {}
    persona_weights = body.get("persona_weights")
    if not persona_weights or not isinstance(persona_weights, dict):
        return jsonify({"error": "persona_weights is required (dict of slug → weight)"}), 400

    agent_count = body.get("agent_count", 200)
    if not isinstance(agent_count, int) or agent_count < 1:
        return jsonify({"error": "agent_count must be a positive integer"}), 400
    agent_count = min(agent_count, 1000)  # safety cap

    # Build agents
    agents = build_agents(persona_weights, count=agent_count)

    # Insert into DB
    created = 0
    for agent in agents:
        execute_returning(
            """
            INSERT INTO agents (experiment_id, name, persona_blend, traits, backstory)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                str(exp_id),
                agent["name"],
                json.dumps(agent["persona_blend"]),
                json.dumps(agent["traits"]),
                agent["backstory"],
            ),
        )
        created += 1

    return jsonify({"agents_created": created})


# ─── GET / ────────────────────────────────────────────────────────────────────

@population_bp.route("", methods=["GET"])
def get_population(exp_id):
    """
    Return the current population for an experiment:
    persona weight distribution + sample agents + total count.
    """
    experiment = _get_experiment(exp_id)
    if not experiment:
        return jsonify({"error": "experiment not found"}), 404

    # Get all agents for this experiment
    agents_rows = query(
        "SELECT * FROM agents WHERE experiment_id = %s ORDER BY created_at",
        (str(exp_id),),
    )

    if not agents_rows:
        return jsonify({"personas": [], "agents": [], "total_agents": 0})

    # Aggregate persona weights from agent blend data
    persona_weight_totals: dict[str, float] = {}
    for row in agents_rows:
        blend = row.get("persona_blend")
        if isinstance(blend, str):
            blend = json.loads(blend)
        if blend:
            for entry in blend:
                slug = entry.get("slug", "")
                influence = entry.get("influence", 0)
                persona_weight_totals[slug] = persona_weight_totals.get(slug, 0) + influence

    # Normalise to get average weights
    total_influence = sum(persona_weight_totals.values()) or 1
    personas = [
        {"slug": slug, "weight": round(w / total_influence, 4)}
        for slug, w in sorted(
            persona_weight_totals.items(), key=lambda x: x[1], reverse=True
        )
    ]

    # Sample up to 5 agents
    sample = [_serialize(row) for row in agents_rows[:5]]

    return jsonify({
        "personas": personas,
        "agents": sample,
        "total_agents": len(agents_rows),
    })


# ─── POST /preview-agent ─────────────────────────────────────────────────────

@population_bp.route("/preview-agent", methods=["POST"])
def preview_agent(exp_id):
    """
    Generate one sample hybrid agent (not saved to DB).
    Body: {persona_weights: {slug: weight, ...}}
    """
    body = request.get_json(force=True) or {}
    persona_weights = body.get("persona_weights")
    if not persona_weights or not isinstance(persona_weights, dict):
        return jsonify({"error": "persona_weights is required (dict of slug → weight)"}), 400

    agents = build_agents(persona_weights, count=1)
    if not agents:
        return jsonify({"error": "could not generate agent"}), 500

    return jsonify({"agent": agents[0]})
