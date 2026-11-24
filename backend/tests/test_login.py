"""Automated integration and unit tests for Login API and JWT-based authentication."""

from datetime import timedelta
import unittest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.security import create_access_token, decode_access_token
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


class TestLoginAndJWTAuthentication(unittest.TestCase):
    """Test suite covering POST /api/v1/auth/login and GET /api/v1/auth/me."""

    @classmethod
    def setUpClass(cls):
        """Initialize test client and create a reusable registered test user."""
        cls.client = TestClient(app)
        cls.test_email = f"login.test.{uuid.uuid4().hex[:8]}@spectrace.dev"
        cls.test_name = "Auth Test User"
        cls.test_password = "SecurePassword#2026!"

        # Register user via the registration endpoint
        res = cls.client.post(
            "/api/v1/auth/register",
            json={
                "name": cls.test_name,
                "email": cls.test_email,
                "password": cls.test_password,
            },
        )
        assert res.status_code == 201, f"Failed to register test user: {res.text}"
        cls.test_user_id = res.json()["id"]

    @classmethod
    def tearDownClass(cls):
        """Clean up the test user from database."""
        with SessionLocal() as db:
            db.execute(delete(User).where(User.email == cls.test_email))
            db.commit()

    def test_successful_login(self):
        """Verify successful login returns signed JWT access token and safe user info."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Token payload checks
        self.assertIn("access_token", data)
        self.assertTrue(len(data["access_token"]) > 20)
        self.assertEqual(data["token_type"], "bearer")
        self.assertGreater(data["expires_in"], 0)

        # Embedded safe user info checks
        self.assertIn("user", data)
        user_info = data["user"]
        self.assertEqual(user_info["id"], self.test_user_id)
        self.assertEqual(user_info["name"], self.test_name)
        self.assertEqual(user_info["email"], self.test_email)
        self.assertIn("created_at", user_info)

        # Ensure token is decodable and contains expected sub claim
        payload = decode_access_token(data["access_token"])
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], str(self.test_user_id))

    def test_login_incorrect_password(self):
        """Verify login fails with 401 when password is incorrect."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.test_email,
                "password": "WrongPassword#999",
            },
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data.get("detail"), "Invalid email or password")
        self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_login_nonexistent_email(self):
        """Verify login fails with 401 and generic message when email does not exist."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "definitely.not.found@spectrace.dev",
                "password": "AnyPassword#123",
            },
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        # Must match the exact error message of incorrect password (anti-enumeration)
        self.assertEqual(data.get("detail"), "Invalid email or password")
        self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_valid_token_accessing_me(self):
        """Verify accessing protected /auth/me returns current user profile."""
        # 1. Login to obtain valid JWT
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password,
            },
        )
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]

        # 2. Access GET /auth/me
        me_res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(me_res.status_code, 200)
        profile = me_res.json()
        self.assertEqual(profile["id"], self.test_user_id)
        self.assertEqual(profile["name"], self.test_name)
        self.assertEqual(profile["email"], self.test_email)
        self.assertIn("created_at", profile)

    def test_missing_token_accessing_me(self):
        """Verify protected /auth/me returns 401 when no token is provided."""
        response = self.client.get("/api/v1/auth/me")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_invalid_token_accessing_me(self):
        """Verify protected /auth/me returns 401 when invalid token is provided."""
        invalid_tokens = [
            "invalid.token.payload",
            "not-a-token-at-all",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered_signature",
        ]

        for bad_token in invalid_tokens:
            response = self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {bad_token}"},
            )
            self.assertEqual(
                response.status_code,
                401,
                f"Expected 401 for bad token '{bad_token[:15]}...', got {response.status_code}",
            )
            self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_expired_token_accessing_me(self):
        """Verify protected /auth/me returns 401 when an expired token is provided."""
        # Create an already expired token (expired 60 seconds ago)
        expired_token = create_access_token(
            subject=self.test_user_id,
            expires_delta=timedelta(seconds=-60),
        )

        # Verify decoding returns None safely
        self.assertIsNone(decode_access_token(expired_token))

        # Access /me with expired token
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers.get("www-authenticate"), "Bearer")

    def test_response_never_exposes_password_or_password_hash(self):
        """Verify that login and /me responses never expose plain or hashed passwords."""
        # Test Login response
        login_res = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.test_email,
                "password": self.test_password,
            },
        )
        self.assertEqual(login_res.status_code, 200)
        login_json = login_res.json()
        login_text = login_res.text

        self.assertNotIn("password", login_json)
        self.assertNotIn("hashed_password", login_json)
        self.assertNotIn("password", login_json["user"])
        self.assertNotIn("hashed_password", login_json["user"])
        self.assertNotIn(self.test_password, login_text)
        self.assertNotIn("$argon2id$", login_text)

        # Test /me response
        token = login_json["access_token"]
        me_res = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_res.status_code, 200)
        me_json = me_res.json()
        me_text = me_res.text

        self.assertNotIn("password", me_json)
        self.assertNotIn("hashed_password", me_json)
        self.assertNotIn(self.test_password, me_text)
        self.assertNotIn("$argon2id$", me_text)


if __name__ == "__main__":
    unittest.main()
