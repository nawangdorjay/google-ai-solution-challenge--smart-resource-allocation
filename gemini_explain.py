"""
gemini_explain.py — Member 2 (AI/ML)
======================================
Generates a human-readable 1-sentence explanation for why a volunteer
was matched to a request. Uses Gemini 1.5 Flash if API key is set,
otherwise falls back to a structured rule-based sentence.

Single GenerativeModel instance is cached at module level to avoid
creating a new connection on every match call.
"""

import os
import logging

log = logging.getLogger("gemini_explain")

# ── Module-level Gemini cache ──────────────────────────────────────────────
_gemini_model = None


def _get_gemini_model():
    """Return cached Gemini model, creating it once if needed."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or len(api_key) < 10 or api_key.lower().startswith("your-"):
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        log.info("Gemini model initialised (cached).")
        return _gemini_model
    except Exception as exc:
        log.warning("Gemini init failed: %s", exc)
        return None


# ── Fallback rule-based explanation ───────────────────────────────────────

def _rule_based(volunteer_name, request_title, skill_score,
                city_match, availability, urgency, reason_tags, distance_km):
    """Build a structured human-readable sentence without any API call."""
    reasons = ", ".join(reason_tags) if reason_tags else "partial skill alignment"
    urg_text = "critical" if urgency == 5 else "high" if urgency >= 4 else "moderate" if urgency == 3 else "low"
    dist_text = f"{distance_km:.0f} km away" if distance_km is not None else "same city" if city_match else "different city"
    avail_text = "is available" if availability else "is currently unavailable"
    skill_pct = int(skill_score * 100)
    return (
        f"{volunteer_name} {avail_text} and matches {skill_pct}% of required skills "
        f"for '{request_title}' ({dist_text}, {urg_text} urgency) — key reasons: {reasons}."
    )


# ── Main public function ───────────────────────────────────────────────────

def explain_match(
    volunteer_name: str,
    request_title: str,
    skill_score: float,
    city_match: bool,
    availability: bool,
    urgency: int,
    reason_tags: list,
    distance_km: float = None,
) -> str:
    """
    Generate a 1-sentence explanation of a volunteer-request match.

    Parameters
    ----------
    volunteer_name  : Name of the matched volunteer.
    request_title   : Title of the NGO request.
    skill_score     : Fraction of required skills matched (0.0 – 1.0).
    city_match      : True if volunteer and request are in the same city / close.
    availability    : True if volunteer is currently available.
    urgency         : Request urgency level (1–5).
    reason_tags     : Short human-readable tags from matcher (e.g. ["Strong skill match"]).
    distance_km     : Computed haversine distance, or None if coordinates were missing.

    Returns
    -------
    str  — A single sentence explanation.
    """
    fallback = lambda: _rule_based(
        volunteer_name, request_title, skill_score,
        city_match, availability, urgency, reason_tags, distance_km,
    )

    model = _get_gemini_model()
    if model is None:
        return fallback()

    dist_text = f"{distance_km:.1f} km" if distance_km is not None else ("same city" if city_match else "different city")

    prompt = (
        "You are an AI volunteer coordinator. Write exactly ONE clear sentence "
        "explaining why this volunteer was matched to the NGO request. "
        "Do NOT include raw numbers or bullet points.\n\n"
        f"Volunteer: {volunteer_name}\n"
        f"Request: {request_title}\n"
        f"Skill match: {int(skill_score * 100)}%\n"
        f"Distance: {dist_text}\n"
        f"Available: {availability}\n"
        f"Urgency: {urgency}/5\n"
        f"Key reasons: {', '.join(reason_tags) if reason_tags else 'partial match'}\n\n"
        "Explanation:"
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 80, "temperature": 0.35},
        )
        text = response.text.strip()
        return text if text else fallback()
    except Exception as exc:
        log.debug("Gemini call failed: %s — using fallback.", exc)
        return fallback()


def batch_explain(match_list: list) -> list:
    """
    Generate explanations for a list of match dicts produced by matcher.get_matches().
    Each item must have keys: volunteer_name, request_title, skill_score, city_match,
    availability, urgency, reason_tags, distance_km.
    Returns the same list with an 'explanation' key filled in.
    """
    for item in match_list:
        item["explanation"] = explain_match(
            volunteer_name=item.get("name", "Volunteer"),
            request_title=item.get("request_title", "Request"),
            skill_score=item.get("breakdown", {}).get("skill", 0),
            city_match=item.get("breakdown", {}).get("distance_score", 0) >= 0.8,
            availability=item.get("breakdown", {}).get("availability", 0) == 1.0,
            urgency=int(item.get("breakdown", {}).get("urgency", 0.6) * 5),
            reason_tags=item.get("reason_tags", []),
            distance_km=item.get("distance_km"),
        )
    return match_list
