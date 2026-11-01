import unittest

from recommender import Item, RecommendationEngine, load_engine, tokenize


class RecommendationEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = load_engine()

    def test_tokenize_normalizes_and_removes_stopwords(self):
        self.assertEqual(tokenize("Python, and Data!"), {"python", "data"})

    def test_relevant_item_ranks_first(self):
        results = self.engine.recommend("machine learning python", top_k=3)
        self.assertEqual(results[0].item.id, "ml-foundations")
        self.assertGreater(results[0].score, results[1].score)

    def test_result_contains_explanation(self):
        result = self.engine.recommend("security networks", top_k=1)[0]
        self.assertIn("security", result.matched_interests)
        self.assertIn("tag_similarity", result.breakdown)

    def test_empty_interests_are_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.recommend("the and of")

    def test_invalid_top_k_is_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.recommend("python", top_k=0)

    def test_catalog_is_nonempty(self):
        self.assertGreaterEqual(len(self.engine.items), 8)
        self.assertTrue(all(isinstance(item, Item) for item in self.engine.items))


if __name__ == "__main__":
    unittest.main()
