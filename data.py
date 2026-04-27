"""
data.py — Member 1 (Data)
Responsible for providing clean, standardised data structures.
Includes sample volunteers, sample request, skill synonym mapping, and DB loader.
"""

# Skill synonym map — Member 1 maintains this.
# Maps raw/informal skill names → canonical skill names used by the matcher.
SYNONYMS = {
    # Medical
    "doctor":       "medical",
    "physician":    "medical",
    "nurse":        "medical",
    "paramedic":    "medical",
    "medic":        "first aid",
    "cpr":          "first aid",
    "first-aid":    "first aid",
    # Education
    "tutor":        "teaching",
    "educator":     "teaching",
    "instructor":   "teaching",
    "trainer":      "teaching",
    # Counselling
    "counsellor":   "counseling",
    "therapist":    "counseling",
    "psychologist": "counseling",
    # Logistics / Transport
    "driver":       "driving",
    "logistics":    "driving",
    "delivery":     "driving",
    # Technology
    "coding":       "it",
    "programming":  "it",
    "tech":         "it",
    "developer":    "it",
    "engineer":     "it",
    # Nutrition
    "diet":         "nutrition",
    "dietitian":    "nutrition",
}

# Sample volunteer dataset — Member 1 maintains this.
# 'id' is required by Member 3's backend and Member 2's matcher output.
SAMPLE_VOLUNTEERS = [
    {
        "id": "v1",
        "name": "Amit Sharma",
        "skills": ["Medical", "Driving", "First Aid"],
        "city": "Delhi",
        "available": True,
        "completed_tasks": 14,
        "rating": 4.7,
    },
    {
        "id": "v2",
        "name": "Riya Mehta",
        "skills": ["educator", "Counseling"],
        "city": "Mumbai",
        "available": True,
        "completed_tasks": 6,
        "rating": 4.2,
    },
    {
        "id": "v3",
        "name": "Rahul Gupta",
        "skills": ["medic", "logistics"],
        "city": "Gurgaon",
        "available": False,
        "completed_tasks": 9,
        "rating": 3.9,
    },
    {
        "id": "v4",
        "name": "Priya Kapoor",
        "skills": ["physician", "nutrition"],
        "city": "Delhi",
        "available": True,
        "completed_tasks": 3,
        "rating": 4.0,
    },
    {
        "id": "v5",
        "name": "Vikram Singh",
        "skills": ["driving", "logistics"],
        "city": "Pune",
        "available": True,
        "completed_tasks": 20,
        "rating": 4.8,
    },
    {
        "id": "v6",
        "name": "Sunita Rao",
        "skills": ["nurse", "first aid", "counseling"],
        "city": "Delhi",
        "available": True,
        "completed_tasks": 22,
        "rating": 4.9,
    },
]

# Sample NGO Request
SAMPLE_REQUEST = {
    "title": "Emergency Medical Camp",
    "required_skills": ["medical", "first aid"],
    "city": "Delhi",
    "urgency": 5,
    "description": "Need medical volunteers urgently."
}

def load_volunteers_from_json(filepath: str) -> list:
    """
    Member 1 utility:
    Read a JSON list of volunteers exported from Google Forms and return cleaned list.
    Falls back to SAMPLE_VOLUNTEERS if the file is missing or malformed.
    """
    import json
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        print(f"Loaded {len(raw_data)} volunteers from {filepath}")
        return raw_data
    except FileNotFoundError:
        print(f"[data.py] File '{filepath}' not found — using SAMPLE_VOLUNTEERS.")
        return SAMPLE_VOLUNTEERS
    except Exception as exc:
        print(f"[data.py] Error reading '{filepath}': {exc} — using SAMPLE_VOLUNTEERS.")
        return SAMPLE_VOLUNTEERS


def load_volunteers_from_db() -> list:
    """
    Member 1 / Member 3 bridge:
    Load available volunteers from SQLite DB (set up by Member 3's database.py).
    Falls back to SAMPLE_VOLUNTEERS if the DB is empty or unavailable.
    """
    import json as _json
    try:
        from database import get_db_connection
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT id, name, skills, city, available FROM volunteers WHERE available = 1"
        ).fetchall()
        conn.close()
        if not rows:
            return SAMPLE_VOLUNTEERS
        volunteers = []
        for row in rows:
            r = dict(row)
            try:
                r["skills"] = _json.loads(r["skills"])
            except Exception:
                r["skills"] = [s.strip() for s in str(r.get("skills", "")).split(",")]
            r["available"] = bool(r.get("available", 1))
            volunteers.append(r)
        return volunteers
    except Exception as exc:
        print(f"[data.py] DB load failed: {exc} — using SAMPLE_VOLUNTEERS.")
        return SAMPLE_VOLUNTEERS

def clean_skills(skills_list):
    """
    Cleans a list of skills by lowercasing, stripping spaces, resolving synonyms, and removing duplicates.
    Example: [" doctor ", "medical", "driving"] -> ["medical", "driving"]
    """
    if not skills_list:
        return []
    
    cleaned = []
    for skill in skills_list:
        clean_skill = str(skill).strip().lower()
        # Resolve synonym if exists
        clean_skill = SYNONYMS.get(clean_skill, clean_skill)
        
        if clean_skill and clean_skill not in cleaned:
            cleaned.append(clean_skill)
    return cleaned
