"""
Prelude API router.
Mounted at /api/prelude in the main Flask app.
"""

from flask import Blueprint, jsonify
from .experiments import experiments_bp
from .brief import brief_bp
from .personas import personas_bp
from .population import population_bp
from .simulation import simulation_bp
from .prediction import prediction_bp
from .calibration import calibration_bp, team_calibration_bp

prelude_bp = Blueprint("prelude", __name__)

# Mount sub-routers
prelude_bp.register_blueprint(experiments_bp, url_prefix="/experiments")
prelude_bp.register_blueprint(brief_bp, url_prefix="/experiments")
prelude_bp.register_blueprint(personas_bp, url_prefix="/personas")
prelude_bp.register_blueprint(population_bp, url_prefix="/experiments/<exp_id>/population")
prelude_bp.register_blueprint(simulation_bp, url_prefix="/experiments/<exp_id>/simulation")
prelude_bp.register_blueprint(prediction_bp, url_prefix="/experiments/<exp_id>")
prelude_bp.register_blueprint(calibration_bp, url_prefix="/experiments/<exp_id>")
prelude_bp.register_blueprint(team_calibration_bp, url_prefix="/team")


@prelude_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Prelude"})
