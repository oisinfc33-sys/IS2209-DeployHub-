import logging
from flask import Blueprint, request, jsonify, render_template
from .weather import get_weather
from .database import save_search, get_recent_searches, get_connection

logger = logging.getLogger(__name__)
main = Blueprint("main", __name__)


@main.route("/")
def index():
    recent = get_recent_searches()
    return render_template("index.html", recent=recent)


@main.route("/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "city parameter is required"}), 400

    data = get_weather(city)

    if "error" not in data:
        try:
            save_search(data["city"], data["country"], data["temperature"], data["conditions"])
        except Exception as e:
            logger.error("Could not save search to database: %s", str(e))

    return jsonify(data)


@main.route("/health")
def health():
    db_ok = False
    try:
        conn = get_connection()
        conn.close()
        db_ok = True
    except Exception:
        pass

    if db_ok:
        return jsonify({"status": "ok", "db": True}), 200
    else:
        return jsonify({"status": "degraded", "db": False}), 503


@main.route("/status")
def status():
    db_ok = False
    recent_count = 0
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM searches")
        recent_count = cur.fetchone()["count"]
        cur.close()
        conn.close()
        db_ok = True
    except Exception as e:
        logger.error("Status page DB error: %s", str(e))

        return render_template("status.html", db_ok=db_ok, recent_count=recent_count)
