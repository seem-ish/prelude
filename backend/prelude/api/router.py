"""
Prelude API router.
Mounted at /api/prelude in the main Flask app.
"""

from flask import Blueprint, jsonify

prelude_bp = Blueprint("prelude", __name__)


@prelude_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Prelude"})


# Sub-routers will be registered here as slices are built:
# from .experiments import experiments_bp
# from .personas import personas_bp
# prelude_bp.register_blueprint(experiments_bp, url_prefix="/experiments")
# prelude_bp.register_blueprint(personas_bp, url_prefix="/personas")
