import unittest

from web_app import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Find your next", response.data)

    def test_form_returns_recommendations(self):
        response = self.client.post("/recommend", data={"interests": "python machine learning"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Practical Machine Learning", response.data)

    def test_json_api_returns_ranked_results(self):
        response = self.client.get("/api/recommend?interests=security+networks")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["recommendations"][0]["id"], "cybersecurity")
        self.assertIn("breakdown", payload["recommendations"][0])

    def test_json_api_validates_input(self):
        response = self.client.get("/api/recommend?interests=the+and")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_route_manifest_is_available(self):
        response = self.client.get("/manus-routes.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["routes"][0]["path"], "/")


if __name__ == "__main__":
    unittest.main()
