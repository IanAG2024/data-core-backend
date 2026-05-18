import unittest

from backend import create_app


class BackendApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_index_exposes_api_summary(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["service"], "buscador")
        self.assertIn("/api/search", data["endpoints"])

    def test_health_reports_memory_backend(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["backend"], "memory")

    def test_documents_list_returns_seeded_items(self):
        response = self.client.get("/api/documents")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(data["total"], 1)
        self.assertGreaterEqual(len(data["items"]), 1)

    def test_search_returns_results(self):
        response = self.client.get("/api/search?q=python")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["query"], "python")
        self.assertGreaterEqual(data["total"], 1)

    def test_categories_and_tags_exist(self):
        categories = self.client.get("/api/categories")
        tags = self.client.get("/api/tags")

        self.assertEqual(categories.status_code, 200)
        self.assertEqual(tags.status_code, 200)
        self.assertGreaterEqual(categories.get_json()["total"], 1)
        self.assertGreaterEqual(tags.get_json()["total"], 1)


if __name__ == "__main__":
    unittest.main()
