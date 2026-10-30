import os
import unittest

os.environ["SECRET_KEY"] = "test-only-key-never-use-in-production-0123456789"
os.environ["MYSQL_USER"] = "test-user"
os.environ["MYSQL_PASSWORD"] = "test-password"
os.environ["MYSQL_DATABASE"] = "rifa_test"

from app import app  # noqa: E402


class SecurityBaselineTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_admin_endpoints_reject_anonymous_requests(self):
        checks = [
            ("GET", "/api/admin/rifas"),
            ("GET", "/api/admin/usuarios"),
            ("POST", "/api/admin/rifas"),
            ("POST", "/api/admin/rifas/1/sorteio"),
        ]
        for method, path in checks:
            with self.subTest(method=method, path=path):
                response = self.client.open(path, method=method, json={})
                self.assertEqual(response.status_code, 401)

    def test_payment_simulation_is_disabled(self):
        response = self.client.post("/api/pagamentos/simular", json={})
        self.assertEqual(response.status_code, 410)

    def test_new_reservations_require_authentication(self):
        response = self.client.post("/api/reservas/criar", json={})
        self.assertEqual(response.status_code, 401)

    def test_authenticated_reservation_creation_is_still_blocked(self):
        import jwt
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "sub": "1",
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=5)).timestamp()),
                "iss": "api-sistema-rifa",
                "aud": "api-sistema-rifa-client",
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        response = self.client.post(
            "/api/reservas/criar",
            json={"rifa_id": 1, "numeros": [1]},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
