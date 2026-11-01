"""Flask web UI for the recommendation engine."""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from recommender import load_engine

app = Flask(__name__)
engine = load_engine()


@app.get("/")
def index():
    return render_template("index.html", recommendations=None, interests="", rating="")


@app.post("/recommend")
def recommend():
    interests = request.form.get("interests", "").strip()
    rating_text = request.form.get("rating", "").strip()
    try:
        preferred_rating = float(rating_text) if rating_text else None
        recommendations = engine.recommend(
            interests,
            top_k=5,
            preferred_rating=preferred_rating,
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
    rating_text = request.args.get("rating", "").strip()
    try:
        preferred_rating = float(rating_text) if rating_text else None
        results = engine.recommend(interests, top_k=5, preferred_rating=preferred_rating)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({
        "recommendations": [
            {
                "id": result.item.id,
                "title": result.item.title,
                "category": result.item.category,
                "description": result.item.description,
                "score": round(result.score, 4),
                "matched_interests": list(result.matched_interests),
                "breakdown": {key: round(value, 4) for key, value in result.breakdown.items()},
            }
            for result in results
        ]
    })


@app.get("/manus-routes.json")
def routes_manifest():
    return jsonify({"routes": [
        {"path": "/", "title": "AI Recommendation Logic"},
        {"path": "/recommend", "title": "Recommendations"},
        {"path": "/api/recommend", "title": "Recommendation API"},
    ]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
