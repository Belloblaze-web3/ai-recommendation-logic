"""Command-line interface for the SignalMatch recommendation engine."""
from __future__ import annotations

import argparse
from collections.abc import Sequence

from recommender import Recommendation, load_engine


def print_recommendations(recommendations: Sequence[Recommendation]) -> None:
    """Print ranked recommendations in a readable terminal format."""
    print("\nRecommended learning resources\n" + "=" * 34)
    for index, recommendation in enumerate(recommendations, 1):
        item = recommendation.item
        matched = ", ".join(recommendation.matched_interests) or "related topics"
        print(f"\n{index}. {item.title} [{item.category}]")
        print(f"   Score: {recommendation.score:.3f} | Rating: {item.rating:.1f}/5")
        print(f"   Why: matches your interests: {matched}")
        print(f"   {item.description}")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser separately so it can be tested or reused."""
    parser = argparse.ArgumentParser(
        description="Find learning resources matching your interests",
    )
    parser.add_argument(
        "--interests",
        help="Comma-separated interests, for example: 'python, AI, data'",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of recommendations to display (default: 5)",
    )
    parser.add_argument(
        "--rating",
        type=float,
        help="Optional preferred item rating from 1 to 5",
    )
    return parser


def main() -> None:
    """Run the interactive or argument-based recommendation flow."""
    parser = build_parser()
    args = parser.parse_args()
    interests = args.interests or input("What are you interested in? ")
    try:
        recommendations = load_engine().recommend(
            interests,
            top_k=args.top,
            preferred_rating=args.rating,
        )
    except ValueError as error:
        parser.error(str(error))
    print_recommendations(recommendations)


if __name__ == "__main__":
    main()
