"""
main.py — Member 3 (Backend API)
Provides REST APIs for managing volunteers, NGO requests, AI matches, and history.
"""

import os
import json
import logging
from flask import Flask, jsonify, request, render_template, send_file

log = logging.getLogger("main")

# Import Backend DB (Member 3)
from database import get_db_connection

# Import Data (Member 2 placeholder — Member 1 will replace with real CSV data)
from data import SAMPLE_VOLUNTEERS, SAMPLE_REQUEST, clean_skills, load_volunteers_from_db

# Import AI Logic (Member 2)
from matcher import get_matches

# Import History Logger (Member 2)
from history_logger import log_result, get_history

app = Flask(__name__)

# ==========================================
# APIs FOR MEMBER 3 (BACKEND INTEGRATION)
# ==========================================

@app.route("/api/add_volunteer", methods=["POST"])
def add_volunteer():
    """API for Member 3: Insert volunteer into SQL database."""
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO volunteers (name, skills, city, available)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], json.dumps(data.get('skills', [])), data['city'],
          data.get('available', True)))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Volunteer added"})


@app.route("/api/add_request", methods=["POST"])
def add_request():
    """API for Member 3: Insert NGO request into SQL database."""
    data = request.json
    conn = get_db_connection()
    req_id = conn.execute('''
        INSERT INTO requests (title, required_skills, city, urgency)
        VALUES (?, ?, ?, ?)
    ''', (data['title'], json.dumps(data.get('required_skills', [])), data['city'],
          data.get('urgency', 3))).lastrowid
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "request_id": req_id})


@app.route("/api/get_matches", methods=["POST"])
def retrieve_matches():
    """
    API for Member 3: Fetches request, gets volunteers from DB (or sample data),
    and calls Member 2's AI matching function.
    Accepts optional query param: ?top_n=5
    """
    req_data = request.json.get("request") if request.json else None
    req_data = req_data or SAMPLE_REQUEST

    top_n = int(request.args.get("top_n", 3))

    # Try to load live volunteers from DB; falls back to sample data automatically
    volunteers = load_volunteers_from_db()

    # Handoff to Member 2's AI algorithm
    ai_results = get_matches(volunteers, req_data, top_n=top_n)

    # Log to history
    try:
        log_result(req_data.get("id", "api"), req_data.get("title", "API Request"), ai_results)
    except Exception as e:
        log.warning("History log failed: %s", e)

    return jsonify({"status": "success", "matches": ai_results, "count": len(ai_results)})


@app.route("/api/assign", methods=["POST"])
def assign_volunteer():
    """API for Member 3: Locks a volunteer to a task in SQL DB."""
    data = request.json
    if not data or not all(k in data for k in ["volunteer_name", "request_title", "score", "confidence"]):
        return jsonify({"status": "error", "message": "Missing required fields."}), 400
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO assignments (volunteer_name, request_title, score, confidence)
        VALUES (?, ?, ?, ?)
    ''', (data['volunteer_name'], data['request_title'], data['score'], data['confidence']))
    conn.execute('''
        UPDATE volunteers SET available = 0 WHERE name = ?
    ''', (data['volunteer_name'],))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Assigned successfully"})


@app.route("/api/assignments", methods=["GET"])
def get_assignments():
    """API for Member 4: Fetch assignments for the dashboard."""
    conn = get_db_connection()
    rows = conn.execute("SELECT id, volunteer_name, request_title, status FROM assignments ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({"status": "success", "assignments": [dict(r) for r in rows]})


@app.route("/api/accept_assignment", methods=["POST"])
def accept_assignment():
    """API for Member 4: Volunteer accepts the task."""
    data = request.json
    assign_id = data.get("id")
    conn = get_db_connection()
    conn.execute("UPDATE assignments SET status = 'accepted' WHERE id = ?", (assign_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Assignment accepted!"})


# ==========================================
# EXTRA APIs (Member 2 / Member 3 shared)
# ==========================================

@app.route("/api/volunteers", methods=["GET"])
def get_volunteers():
    """API for Member 4: Fetch all volunteers to render in the UI."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM volunteers ORDER BY id DESC").fetchall()
    conn.close()
    vols = []
    for r in rows:
        d = dict(r)
        try:
            d["skills"] = json.loads(d["skills"])
        except:
            d["skills"] = [s.strip() for s in str(d.get("skills", "")).split(",")]
        vols.append({
            "id": d["id"],
            "name": d["name"],
            "skills": d["skills"],
            "location": d.get("city", "Unknown"),
            "status": "available" if d.get("available") else "matched",
            "score": 85,  # Dummy base score for UI list
            "avatar": "teal",
            "joined": "Recent"
        })
    return jsonify({"status": "success", "volunteers": vols})


@app.route("/api/requests", methods=["GET"])
def get_requests():
    """API for Member 4: Fetch all NGO requests to render in the UI."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM requests ORDER BY id DESC").fetchall()
    conn.close()
    reqs = []
    for r in rows:
        d = dict(r)
        try:
            skills = json.loads(d.get("required_skills", "[]"))
        except:
            skills = []
        reqs.append({
            "id": d["id"],
            "org": d.get("title", "").split(" — ")[0] if " — " in d.get("title", "") else d.get("title", "NGO"),
            "skills": skills,
            "location": d.get("city", "Unknown"),
            "urgency": "High" if d.get("urgency", 3) >= 4 else "Medium",
            "vols": 5,
            "desc": d.get("title", "NGO Request")
        })
    return jsonify({"status": "success", "requests": reqs})

@app.route("/api/health", methods=["GET"])
def health_check():
    """Liveness check — used by Member 4's frontend and Docker HEALTHCHECK."""
    return jsonify({"status": "ok", "version": "1.0", "module": "simple_ml"})


@app.route("/api/get_history", methods=["GET"])
def get_match_history():
    """Return the last 30 match results logged by Member 2's history_logger."""
    history = get_history()
    return jsonify({"status": "success", "count": len(history), "history": history})


@app.route("/api/retrain", methods=["POST"])
def retrain_model():
    """Trigger Member 2's model to retrain (deletes old pkl, retrains fresh)."""
    try:
        from model import VolunteerMatchModel, DEFAULT_MODEL_PATH
        import os
        if os.path.exists(DEFAULT_MODEL_PATH):
            os.remove(DEFAULT_MODEL_PATH)
        m = VolunteerMatchModel()
        m.train()
        return jsonify({"status": "success", "message": "Model retrained successfully."})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Update settings like API keys dynamically."""
    data = request.json
    api_key = data.get("gemini_api_key")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        return jsonify({"status": "success", "message": "API Key updated successfully."})
    return jsonify({"status": "error", "message": "No API Key provided."}), 400

# ==========================================
# FRONTEND DASHBOARD (MEMBER 4)
# ==========================================

@app.route("/", methods=["GET"])
def dashboard():
    """Render Member 4's HTML UI and print matches to terminal."""
    try:
        # Load live volunteers from DB (same as /api/get_matches)
        volunteers = load_volunteers_from_db()

        # Generate matches using Member 2's AI
        results = get_matches(volunteers, SAMPLE_REQUEST)

        # 1. Print result in terminal
        print(f"\n--- NEW MATCHING RESULT FOR: {SAMPLE_REQUEST.get('title')} ---")
        print(json.dumps(results, indent=2))
        print("----------------------------------------------------------------\n")

        # 2. Store result in JSON file via history logger (single source of truth)
        log_result(
            SAMPLE_REQUEST.get("id", "demo"),
            SAMPLE_REQUEST.get("title", "Unknown Request"),
            results
        )

        return send_file("hack2.html")
    except Exception as e:
        return f"<h1>Error loading UI</h1><p>{str(e)}</p>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # CLI print handled in simple testing, here we just boot the App
    print(f"Starting Backend API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
