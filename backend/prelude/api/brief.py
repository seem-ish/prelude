"""
Prelude — Brief assist endpoint
POST /api/prelude/experiments/assist
"""

import os
from flask import Blueprint, request, jsonify

brief_bp = Blueprint("brief", __name__)

ASSIST_PROMPTS = {
    "problem": (
        "You are helping a product manager write a clear experiment brief.\n"
        "They are working on a {category} product: \"{product_context}\".\n\n"
        "Write a specific, concrete problem statement for their brief.\n"
        "2-3 sentences. Include a number or metric if possible.\n"
        "PM-friendly language. Focus on what users fail to do and why it matters.\n"
        "Return only the suggested text, no preamble."
    ),
    "variant_a": (
        "You are helping a PM write a clear A/B experiment brief.\n"
        "Product: {category} — \"{product_context}\"\n"
        "Problem: {problem}\n\n"
        "Write a concrete description of Variant A (the more structured/guided option).\n"
        "2-3 sentences. Describe what the user sees and experiences.\n"
        "Return only the suggested text, no preamble."
    ),
    "variant_b": (
        "You are helping a PM write a clear A/B experiment brief.\n"
        "Product: {category} — \"{product_context}\"\n"
        "Problem: {problem}\n"
        "Variant A: {variant_a}\n\n"
        "Write a concrete description of Variant B (meaningfully different from A).\n"
        "2-3 sentences. Describe what the user sees and experiences.\n"
        "Return only the suggested text, no preamble."
    ),
}


@brief_bp.route("/assist", methods=["POST"])
def assist():
    body   = request.get_json(force=True) or {}
    field  = body.get("field", "")
    ctx    = body.get("context", {})

    if field not in ASSIST_PROMPTS:
        return jsonify({"error": f"Unknown field: {field}"}), 400

    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key or api_key == "placeholder":
        return jsonify({
            "suggestion": None,
            "error": "LLM_API_KEY not configured. Add your Anthropic API key to .env to enable AI suggestions."
        }), 200

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = ASSIST_PROMPTS[field].format(
            category        = ctx.get("category", "software"),
            product_context = ctx.get("product_context", ""),
            problem         = ctx.get("problem", ""),
            variant_a       = ctx.get("variant_a", ""),
        )

        message = client.messages.create(
            model      = os.environ.get("LLM_MODEL_NAME", "claude-sonnet-4-20250514"),
            max_tokens = 300,
            messages   = [{"role": "user", "content": prompt}]
        )
        suggestion = message.content[0].text.strip()
        return jsonify({"suggestion": suggestion})

    except Exception as e:
        return jsonify({"error": str(e), "suggestion": None}), 500
