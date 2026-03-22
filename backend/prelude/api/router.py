"""
Prelude API router.
Mounted at /api/prelude in the main Flask app.
"""

from flask import Blueprint, jsonify
from .experiments import experiments_bp

prelude_bp = Blueprint("prelude", __name__)

# Mount sub-routers
prelude_bp.register_blueprint(experiments_bp, url_prefix="/experiments")


@prelude_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Prelude"})
