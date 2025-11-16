from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/status")
def status():
    return jsonify({"status": "Admin OK"})
