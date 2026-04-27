"""
model.py — Member 2 (AI/ML)
==============================
Logistic Regression model for volunteer-to-request matching.
Trained on a richer synthetic dataset with 5 features.
Features: [skill_score, distance_score, availability_score, urgency_score, experience_score]
"""

import numpy as np
import pickle
import os
import logging

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

log = logging.getLogger("model")

# Absolute path so the .pkl is always found regardless of CWD or Docker
_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(_DIR, "lite_model.pkl")

FEATURE_NAMES = [
    "skill_score",
    "distance_score",
    "availability_score",
    "urgency_score",
    "experience_score",
]


def _generate_synthetic_data():
    """
    Generate a richer 60-row synthetic dataset.
    Features: [skill_score, distance_score, availability_score, urgency_score, experience_score]
    Label: 1 = Good match, 0 = Bad match
    """
    # fmt: off
    X = np.array([
        # Perfect matches — all features high
        [1.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 0.8, 1.0],
        [1.0, 1.0, 1.0, 0.6, 0.8],
        [0.9, 1.0, 1.0, 1.0, 0.9],
        [0.9, 0.8, 1.0, 0.8, 1.0],
        [1.0, 0.8, 1.0, 0.6, 0.7],
        [0.8, 1.0, 1.0, 1.0, 0.8],
        [0.8, 0.8, 1.0, 0.8, 1.0],
        [0.8, 1.0, 1.0, 0.6, 0.6],
        [1.0, 0.5, 1.0, 1.0, 0.9],

        # Good matches — mostly high
        [0.7, 1.0, 1.0, 0.8, 0.7],
        [0.7, 0.8, 1.0, 0.8, 0.8],
        [0.6, 1.0, 1.0, 1.0, 0.9],
        [0.6, 0.8, 1.0, 0.6, 0.7],
        [0.7, 0.5, 1.0, 1.0, 1.0],
        [0.8, 0.5, 1.0, 0.6, 0.6],
        [0.6, 1.0, 1.0, 0.4, 0.8],
        [0.5, 1.0, 1.0, 1.0, 1.0],
        [0.5, 0.8, 1.0, 0.8, 0.9],
        [0.6, 0.5, 1.0, 0.8, 0.8],

        # Borderline — moderate signals
        [0.5, 0.5, 1.0, 0.6, 0.5],
        [0.4, 1.0, 1.0, 0.6, 0.5],
        [0.5, 0.8, 1.0, 0.4, 0.4],
        [0.4, 0.5, 1.0, 0.8, 0.5],
        [0.3, 1.0, 1.0, 1.0, 0.6],
        [0.5, 0.5, 1.0, 0.4, 0.3],
        [0.4, 0.8, 1.0, 0.4, 0.3],
        [0.3, 0.8, 1.0, 0.6, 0.5],
        [0.6, 0.0, 1.0, 1.0, 0.7],
        [0.5, 0.0, 1.0, 0.8, 0.6],

        # Bad matches — unavailable
        [1.0, 1.0, 0.0, 1.0, 1.0],
        [1.0, 0.8, 0.0, 0.8, 1.0],
        [0.8, 1.0, 0.0, 1.0, 0.9],
        [0.7, 0.8, 0.0, 0.8, 0.8],
        [0.6, 0.5, 0.0, 0.6, 0.7],
        [0.5, 1.0, 0.0, 0.6, 0.5],
        [1.0, 0.0, 0.0, 1.0, 0.8],
        [0.8, 0.5, 0.0, 0.8, 0.6],
        [0.4, 0.8, 0.0, 1.0, 0.5],
        [0.6, 0.8, 0.0, 0.4, 0.4],

        # Bad matches — poor skill
        [0.0, 1.0, 1.0, 1.0, 1.0],
        [0.1, 1.0, 1.0, 0.8, 0.9],
        [0.2, 1.0, 1.0, 0.6, 0.8],
        [0.0, 0.8, 1.0, 0.8, 0.7],
        [0.1, 0.5, 1.0, 1.0, 0.6],
        [0.2, 0.5, 1.0, 0.6, 0.5],
        [0.1, 0.0, 1.0, 1.0, 0.5],
        [0.2, 0.8, 1.0, 0.4, 0.3],
        [0.0, 0.0, 1.0, 1.0, 0.4],
        [0.2, 0.0, 1.0, 0.8, 0.3],

        # Bad matches — far away and low skill
        [0.3, 0.0, 1.0, 0.6, 0.4],
        [0.2, 0.0, 1.0, 0.4, 0.3],
        [0.1, 0.0, 0.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 1.0, 0.6],
        [0.2, 0.0, 0.0, 0.8, 0.4],
        [0.1, 0.0, 0.0, 0.6, 0.3],
        [0.0, 0.5, 0.0, 0.4, 0.2],
        [0.2, 0.5, 0.0, 0.2, 0.2],
        [0.0, 0.0, 0.0, 0.2, 0.1],
        [0.1, 0.0, 0.0, 0.2, 0.2],
    ])

    y = np.array([
        # Perfect        (10)
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        # Good           (10)
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        # Borderline     (10) → mixed
        1, 1, 0, 0, 1, 0, 0, 0, 1, 0,
        # Unavailable    (10)
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        # Poor skill     (10)
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        # Far + low      (10)
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ])
    # fmt: on
    return X, y


class VolunteerMatchModel:
    """
    Logistic Regression pipeline (scaler + classifier) for volunteer matching.
    5 features: skill, distance, availability, urgency, experience.
    """

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.is_trained = False
        # sklearn Pipeline: scales features → LogReg
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=2.0, max_iter=500, random_state=42)),
        ])
        self.load_or_train()

    # ── Persistence ──────────────────────────────────────────────────────────

    def load_or_train(self):
        """Load persisted model from disk; train fresh if missing or corrupt."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.pipeline = pickle.load(f)
                self.is_trained = True
                log.info("Model loaded from %s", self.model_path)
                return
            except Exception as exc:
                log.warning("Could not load model (%s) — retraining.", exc)
        self.train()

    def train(self):
        """Train on synthetic data and persist to disk."""
        X, y = _generate_synthetic_data()
        self.pipeline.fit(X, y)
        self.is_trained = True
        log.info(
            "Model trained on %d samples. Feature names: %s",
            len(y), FEATURE_NAMES,
        )
        self._save()

    def retrain(self):
        """Public re-train hook (called by main.py /api/retrain endpoint)."""
        self.train()

    def _save(self):
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.pipeline, f)
            log.info("Model saved to %s", self.model_path)
        except Exception as exc:
            log.warning("Could not save model: %s", exc)

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_score(self, feature_vector: list) -> float:
        """
        Accept a 5-element feature vector and return probability of being a good match (0–1).
        Feature order: [skill_score, distance_score, availability_score, urgency_score, experience_score]
        """
        if not self.is_trained:
            self.load_or_train()
        X = np.array(feature_vector, dtype=float).reshape(1, -1)
        probability = self.pipeline.predict_proba(X)[0][1]
        return float(probability)

    @staticmethod
    def feature_names() -> list:
        return list(FEATURE_NAMES)
