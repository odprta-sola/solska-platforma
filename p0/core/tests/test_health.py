from django.test import TestCase


class HealthTests(TestCase):
    def test_health_ok(self):
        response = self.client.get("/p0/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_ne_dovoli_pisanja(self):
        response = self.client.post("/p0/api/v1/health")
        self.assertEqual(response.status_code, 405)
