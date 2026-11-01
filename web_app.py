"""Flask web UI and JSON API for the SignalMatch engine."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from recommender import RecommendationEngine, load_engine

DEFAULT_TOP_K = 5
MAX_TOP_K = 20


def _parse_rating(value: str) -> float | None:
    """Parse an optional rating and return a user-facing validation error when needed."""
    if not value.strip():
        return None
    try:
        rating = float(value)
    except ValueError as exc:
        raise ValueError("Preferred rating must be a number between 1 and 5") from exc
    if not 1 <= rating <= 5:
        raise ValueError("Preferred rating must be between 1 and 5")
    return rating


def _parse_top_k(value: str | None) -> int:
    """Parse a bounded result count for the API."""
    if value is None or not value.strip():
        return DEFAULT_TOP_K
    try:
        top_k = int(value)
    except ValueError as exc:
        raise ValueError(f"top_k must be an integer between 1 and {MAX_TOP_K}") from exc
    if not 1 <= top_k <= MAX_TOP_K:
        raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}")
    return top_k


def _serialize_recommendation(result: Any) -> dict[str, Any]:
    """Convert a recommendation dataclass into a stable API response object."""
    return {
        "id": result.item.id,
        "title": result.item.title,
        "category": result.item.category,
        "description": result.item.description,
        "score": round(result.score, 4),
        "matched_interests": list(result.matched_interests),
        "breakdown": {key: round(value, 4) for key, value in result.breakdown.items()},
    }


def create_app(catalog_path: str | Path | None = None) -> Flask:
    """Create and configure the Flask application.

    An app factory keeps the web layer easy to test and allows deployments to
    provide a catalog path without modifying application code.
    """
    app = Flask(__name__)
    engine: RecommendationEngine = load_engine(catalog_path)

    @app.get("/")
    def index():
        return render_template("index.html", recommendations=None, interests="", rating="")

    @app.post("/recommend")
    def recommend():
        interests = request.form.get("interests", "").strip()
        rating_text = request.form.get("rating", "").strip()
        try:
            recommendations = engine.recommend(
                interests,
                top_k=DEFAULT_TOP_K,
                preferred_rating=_parse_rating(rating_text),
            )
            error = None
        except ValueError as exc:
            recommendations = []
            error = str(exc)
        return render_template(
            "index.html",
            recommendations=recommendations,
            interests=interests,
            rating=rating_text,
            error=error,
        )

    @app.get("/api/recommend")
    def api_recommend():
        interests = request.args.get("interests", "").strip()
        try:
            results = engine.recommend(
                interests,
                top_k=_parse_top_k(request.args.get("top_k")),
                preferred_rating=_parse_rating(request.args.get("rating", "")),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"recommendations": [_serialize_recommendation(result) for result in results]})

    @app.get("/manus-routes.json")
    def routes_manifest():
        return jsonify({"routes": [
            {"path": "/", "title": "AI Recommendation Logic"},
            {"path": "/recommend", "title": "Recommendations"},
            {"path": "/api/recommend", "title": "Recommendation API"},
        ]})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
