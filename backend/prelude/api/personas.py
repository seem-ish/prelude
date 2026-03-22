"""
Prelude — Personas API
GET  /api/prelude/personas                list all (optionally filter by cluster)
GET  /api/prelude/personas/<slug>         get single persona by slug
"""

from flask import Blueprint, request, jsonify
from prelude.agents.persona_library import PERSONA_LIBRARY, PERSONAS_BY_SLUG, PERSONAS_BY_CLUSTER

personas_bp = Blueprint("personas", __name__)


@personas_bp.route("", methods=["GET"])
def list_personas():
    cluster = request.args.get("cluster")
    if cluster:
        results = PERSONAS_BY_CLUSTER.get(cluster, [])
    else:
        results = PERSONA_LIBRARY
    return jsonify(results)


@personas_bp.route("/<slug>", methods=["GET"])
def get_persona(slug):
    persona = PERSONAS_BY_SLUG.get(slug)
    if not persona:
        return jsonify({"error": "persona not found"}), 404
    return jsonify(persona)
