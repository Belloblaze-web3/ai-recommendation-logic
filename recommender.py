"""Explainable, content-based recommendation engine."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

STOPWORDS = {
    "a", "an", "and", "for", "from", "in", "into", "of", "on", "or", "the", "to", "with"
}


def tokenize(text: str) -> set[str]:
    """Convert free text into normalized, meaningful tokens."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 1}


@dataclass(frozen=True)
class Item:
    id: str
    title: str
    category: str
    description: str
    tags: tuple[str, ...]
    rating: float
    popularity: float

    @classmethod
    def from_dict(cls, raw: dict) -> "Item":
        return cls(
            id=raw["id"], title=raw["title"], category=raw["category"],
            description=raw["description"], tags=tuple(raw["tags"]),
            rating=float(raw["rating"]), popularity=float(raw["popularity"]),
        )


@dataclass(frozen=True)
class Recommendation:
    item: Item
    score: float
    matched_interests: tuple[str, ...]
    breakdown: dict[str, float]


class RecommendationEngine:
    """Rank catalog items by similarity to a user profile."""

    def __init__(self, items: Sequence[Item]):
        if not items:
            raise ValueError("The catalog must contain at least one item")
        self.items = tuple(items)

    @staticmethod
    def _jaccard(left: set[str], right: set[str]) -> float:
        if not left and not right:
            return 0.0
        return len(left & right) / len(left | right)

    @staticmethod
    def _rating_alignment(user_rating: float | None, item_rating: float) -> float:
        if user_rating is None:
            return 0.75
        # A user preference of 5 means highly rated items are preferred;
        # a preference of 1 makes the rating component intentionally neutral.
        preference = max(1.0, min(5.0, user_rating))
        return 1.0 - abs(preference - item_rating) / 4.0

    def recommend(
        self,
        interests: Iterable[str] | str,
        top_k: int = 5,
        minimum_score: float = 0.0,
        preferred_rating: float | None = None,
    ) -> list[Recommendation]:
        if isinstance(interests, str):
            interest_text = interests
        else:
            interest_text = " ".join(interests)
        user_tokens = tokenize(interest_text)
        if not user_tokens:
            raise ValueError("Enter at least one meaningful interest")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        results: list[Recommendation] = []
        for item in self.items:
            tag_tokens = tokenize(" ".join(item.tags))
            item_tokens = tokenize(f"{item.title} {item.description} {item.category}")
            tag_similarity = self._jaccard(user_tokens, tag_tokens)
            keyword_similarity = self._jaccard(user_tokens, item_tokens)
            rating_alignment = self._rating_alignment(preferred_rating, item.rating)
            popularity_score = max(0.0, min(1.0, item.popularity))
            score = (
                0.55 * tag_similarity
                + 0.25 * keyword_similarity
                + 0.15 * rating_alignment
                + 0.05 * popularity_score
            )
            matched = tuple(sorted(user_tokens & (tag_tokens | item_tokens)))
            if score >= minimum_score:
                results.append(Recommendation(
                    item=item,
                    score=score,
                    matched_interests=matched,
                    breakdown={
                        "tag_similarity": tag_similarity,
                        "keyword_similarity": keyword_similarity,
                        "rating_alignment": rating_alignment,
                        "popularity": popularity_score,
                    },
                ))
        return sorted(results, key=lambda result: (-result.score, result.item.title))[:top_k]


def load_engine(catalog_path: str | Path | None = None) -> RecommendationEngine:
    path = Path(catalog_path) if catalog_path else Path(__file__).with_name("catalog.json")
    with path.open(encoding="utf-8") as file:
        items = [Item.from_dict(raw) for raw in json.load(file)]
    return RecommendationEngine(items)
