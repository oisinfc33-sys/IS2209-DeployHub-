import uuid
import logging
import time
from flask import Blueprint, request, jsonify, render_template, g
from .weather import get_weather
from .database import save_search, get_recent_searches, get_connection

logger = logging.getLogger(__name__)
main = Blueprint("main", __name__)

@main.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

@main.after_request
def after_request(response):
    elapsed = round((time.time() - g.start_time) * 1000, 2)
    logger.info({
        "event": "request",
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "ms": elapsed
    })
    response.headers["X-Request-ID"] = g.request_id
    return response

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
            save_search(data["city"], data["country"], data["temperature"], data["description"])
        except Exception as e:
            logger.error({"event": "db_save_error", "error": str(e)})

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
    status = "ok" if db_ok else "degraded"
    return jsonify({"status": status, "db": db_ok}), 200 if db_ok else 503

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
    except Exception:
        pass
    return render_template("status.html", db_ok=db_ok, recent_count=recent_count)