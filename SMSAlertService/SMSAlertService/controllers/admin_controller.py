from flask import Blueprint

admin_bp = Blueprint('admin_controller', __name__)


@admin_bp.route("/admin")
def admin():
    # TODO: Admin tools
    return 'Forbidden', 403

