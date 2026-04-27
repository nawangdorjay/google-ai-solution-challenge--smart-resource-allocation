"""
matcher.py — Member 2 (AI/ML)
================================
Hybrid volunteer-to-request matching engine.
Combines:
  1. Rule-based feature engineering  (transparent, auditable)
  2. Logistic Regression ML score    (learned from synthetic data)
  3. Gemini AI explanation           (human-readable output)

Note: Distance is computed using city string matching only (no GPS coordinates).

Public API
----------
  get_matches(volunteers, request, top_n=3)
      → list of match dicts, sorted descending by score

Match dict keys
---------------
  volunteer_id    str    — unique identifier (id field or name)
  name            str    — volunteer display name
  score           float  — final hybrid score (0–1)
  confidence      str    — "High" | "Medium" | "Low"
  breakdown       dict   — individual feature scores
  reason_tags     list   — human-readable tags
  explanation     str    — Gemini / rule-based sentence
"""

import logging

from model import VolunteerMatchModel
from data import clean_skills
from gemini_explain import explain_match

log = logging.getLogger("matcher")

# Singleton ML model — trained once at import time
_ml_model = VolunteerMatchModel()


# ── Feature engineering helpers ───────────────────────────────────────────

def _skill_score(vol_skills: list, req_skills: list) -> float:
    """Jaccard-influenced skill overlap (0–1). Returns 0 if no req skills."""
    if not req_skills:
        return 0.0
    matched = [s for s in req_skills if s in vol_skills]
    return len(matched) / len(req_skills)


def _distance_score(vol: dict, req: dict) -> tuple[float, None]:
    """
    Returns (distance_score, None) based on city string matching.
    Score:  1.0  exact same city
            0.5  different city (partial credit for willingness)
            0.0  city completely missing
    """
    v_city = str(vol.get("city", "")).strip().lower()
    r_city = str(req.get("city", "")).strip().lower()

    if not v_city or not r_city:
        return 0.0, None
    if v_city == r_city:
        return 1.0, None
    return 0.5, None


def _experience_score(vol: dict) -> float:
    """
    Lightweight proxy for volunteer experience (0–1).
    Uses completed_tasks if present; falls back to rating field.
    """
    tasks = vol.get("completed_tasks")
    if tasks is not None:
        # Sigmoid-like: 10 tasks → ~0.7, 20 tasks → ~0.9, 0 tasks → 0.3
        return min(1.0, 0.3 + (float(tasks) / (float(tasks) + 15)) * 0.7)

    rating = vol.get("rating")
    if rating is not None:
        return round(float(rating) / 5.0, 2)

    return 0.5  # default neutral


# ── Main matching function ────────────────────────────────────────────────

def get_matches(volunteers: list, request: dict, top_n: int = 3) -> list:
    """
    Score and rank all volunteers for a given request.

    Parameters
    ----------
    volunteers  : list of volunteer dicts (from Member 1's data or DB)
    request     : NGO request dict
    top_n       : number of top results to return (default 3, max 10)

    Returns
    -------
    List of match dicts, sorted descending by score. Length ≤ top_n.
    """
    if not volunteers or not request:
        log.warning("get_matches called with empty volunteers or request.")
        return []

    top_n = min(max(int(top_n), 1), 10)  # clamp 1–10
    req_skills  = clean_skills(request.get("required_skills", []))
    req_urgency = int(request.get("urgency", 3))
    req_title   = request.get("title", "Unknown Request")

    results = []

    for vol in volunteers:
        vol_skills    = clean_skills(vol.get("skills", []))
        vol_available = bool(vol.get("available", False))
        vol_name      = vol.get("name", "Unknown")
        vol_id        = str(vol.get("id", vol_name))  # Member 3/4 use "id"

        # ── 1. Feature Engineering ─────────────────────────────────────────

        sk_score   = _skill_score(vol_skills, req_skills)

        # Filter out completely irrelevant volunteers early (< 15% skill match)
        # This is a soft threshold — low skill but very close / experienced volunteers
        # are still considered if other features compensate.
        if sk_score < 0.15:
            continue

        dist_score, _ = _distance_score(vol, request)
        avail_score = 1.0 if vol_available else 0.0
        urg_score   = round(req_urgency / 5.0, 2)
        exp_score   = _experience_score(vol)

        feature_vector = [sk_score, dist_score, avail_score, urg_score, exp_score]

        # ── 2. Hybrid Scoring ──────────────────────────────────────────────

        ml_score = _ml_model.predict_score(feature_vector)

        # Transparent weighted rule score
        rule_score = (
            0.45 * sk_score
            + 0.20 * dist_score
            + 0.15 * avail_score
            + 0.10 * urg_score
            + 0.10 * exp_score
        )

        # Blend: ML carries 55%, rules carry 45%
        final_score = round(0.55 * ml_score + 0.45 * rule_score, 3)

        # ── 3. Confidence Label ────────────────────────────────────────────

        if final_score >= 0.72:
            confidence = "High"
        elif final_score >= 0.48:
            confidence = "Medium"
        else:
            confidence = "Low"

        # ── 4. Reason Tags ─────────────────────────────────────────────────

        reason_tags = []
        if sk_score >= 0.8:
            reason_tags.append("Excellent skill match")
        elif sk_score >= 0.5:
            reason_tags.append("Strong skill match")
        elif sk_score >= 0.3:
            reason_tags.append("Partial skill match")

        if dist_score == 1.0:
            reason_tags.append("Same city")
        elif dist_score > 0:
            reason_tags.append("Different city (remote contribution)")

        if avail_score == 1.0:
            reason_tags.append("Available now")
        else:
            reason_tags.append("Currently unavailable")

        if req_urgency >= 5:
            reason_tags.append("Critical urgency")
        elif req_urgency >= 4:
            reason_tags.append("High urgency")

        if exp_score >= 0.7:
            reason_tags.append("Experienced volunteer")

        # ── 5. Gemini / Rule Explanation ──────────────────────────────────

        city_match_bool = dist_score >= 1.0
        explanation = explain_match(
            volunteer_name=vol_name,
            request_title=req_title,
            skill_score=sk_score,
            city_match=city_match_bool,
            availability=vol_available,
            urgency=req_urgency,
            reason_tags=reason_tags,
            distance_km=None,  # no coordinates
        )

        # ── 6. Result Dict ─────────────────────────────────────────────────

        results.append({
            "volunteer_id": vol_id,
            "name":         vol_name,
            "score":        final_score,
            "confidence":   confidence,
            "breakdown": {
                "skill":        round(sk_score, 3),
                "distance":     round(dist_score, 3),
                "availability": avail_score,
                "urgency":      urg_score,
                "experience":   round(exp_score, 3),
            },
            "reason_tags":  reason_tags,
            "explanation":  explanation,
        })

    # ── 7. Sort & Return Top-N ─────────────────────────────────────────────

    results.sort(key=lambda x: x["score"], reverse=True)
    log.info(
        "Matched %d volunteers → %d results for '%s' (top_n=%d)",
        len(volunteers), len(results), req_title, top_n,
    )
    return results[:top_n]
