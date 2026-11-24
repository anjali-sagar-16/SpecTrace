"""Automated integration and unit tests for the User Registration API."""

import unittest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.security import verify_password
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


class TestUserRegistrationAPI(unittest.TestCase):
    """Test suite covering the /api/v1/auth/register endpoint."""

    @classmethod
    def setUpClass(cls):
        """Initialize the FastAPI test client."""
        cls.client = TestClient(app)

    def setUp(self):
        """Track test user emails created during tests for reliable cleanup."""
        self.created_emails = []

    def tearDown(self):
        """Clean up any users created during tests to maintain database cleanliness."""
        if self.created_emails:
            with SessionLocal() as db:
                for email in self.created_emails:
                    db.execute(delete(User).where(User.email == email))
                db.commit()

    def test_successful_registration(self):
        """Verify successful registration returns 201 Created and safe user metadata."""
        test_email = f"reg.success.{uuid.uuid4().hex[:8]}@spectrace.dev"
        self.created_emails.append(test_email)
        raw_password = "SecurePassword2026!"

        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Jane Engineer",
                "email": test_email,
                "password": raw_password,
            },
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()

        # Check returned attributes
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Jane Engineer")
        self.assertEqual(data["email"], test_email)
        self.assertIn("created_at", data)

        # Security check: passwords must never appear in API responses
        self.assertNotIn("password", data)
        self.assertNotIn("hashed_password", data)

        # Verify database record persistence and password hashing
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == test_email))
            self.assertIsNotNone(user, "User was not persisted to the database")
            self.assertEqual(user.name, "Jane Engineer")
            self.assertNotEqual(user.hashed_password, raw_password)
            self.assertTrue(user.hashed_password.startswith("$argon2id$"))
            self.assertTrue(verify_password(raw_password, user.hashed_password))

    def test_password_is_stored_as_argon2_hash(self):
        """Verify that stored password hash uses Argon2id format and verifies correctly."""
        test_email = f"reg.hash.{uuid.uuid4().hex[:8]}@spectrace.dev"
        self.created_emails.append(test_email)
        raw_password = "Argon2TestSecret#2026"

        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Hash Verification User",
                "email": test_email,
                "password": raw_password,
            },
        )
        self.assertEqual(response.status_code, 201)

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == test_email))
            self.assertIsNotNone(user)
            # Must be an Argon2id formatted string
            self.assertTrue(
                user.hashed_password.startswith("$argon2id$"),
                f"Password hash does not start with $argon2id$: {user.hashed_password[:20]}",
            )
            # Verification must succeed with the original password
            self.assertTrue(verify_password(raw_password, user.hashed_password))
            # Verification must fail with an incorrect password
            self.assertFalse(verify_password("WrongPassword#999", user.hashed_password))

    def test_duplicate_email_rejection(self):
        """Verify that registering with an existing email returns 409 Conflict."""
        test_email = f"reg.dup.{uuid.uuid4().hex[:8]}@spectrace.dev"
        self.created_emails.append(test_email)

        # First registration must succeed
        res1 = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "First User",
                "email": test_email,
                "password": "ValidPassword#123",
            },
        )
        self.assertEqual(res1.status_code, 201)

        # Second registration with duplicate email must fail with 409 Conflict
        res2 = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Second User Same Email",
                "email": test_email,
                "password": "AnotherPassword#456",
            },
        )
        self.assertEqual(res2.status_code, 409)
        self.assertIn("already exists", res2.json().get("detail", ""))

        # Also test rejection against the existing seed test user
        res_seed = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Seed Impersonator",
                "email": "test.developer@spectrace.dev",
                "password": "SomePassword#789",
            },
        )
        self.assertEqual(res_seed.status_code, 409)
        self.assertIn("already exists", res_seed.json().get("detail", ""))

    def test_invalid_email_rejection(self):
        """Verify that malformed email addresses are rejected with 422 Unprocessable Entity."""
        invalid_emails = [
            "not-an-email",
            "missing-domain@",
            "@no-local-part.com",
            "spaces in email@domain.com",
            "",
        ]

        for invalid_email in invalid_emails:
            response = self.client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Invalid Email User",
                    "email": invalid_email,
                    "password": "ValidPassword#123",
                },
            )
            self.assertEqual(
                response.status_code,
                422,
                f"Expected 422 for invalid email '{invalid_email}', got {response.status_code}",
            )

    def test_empty_name_rejection(self):
        """Verify that empty or whitespace-only names are rejected with 422 Unprocessable Entity."""
        invalid_names = ["", "   ", "\t  \n"]

        for invalid_name in invalid_names:
            response = self.client.post(
                "/api/v1/auth/register",
                json={
                    "name": invalid_name,
                    "email": "valid.user@spectrace.dev",
                    "password": "ValidPassword#123",
                },
            )
            self.assertEqual(
                response.status_code,
                422,
                f"Expected 422 for empty/whitespace name '{invalid_name}', got {response.status_code}",
            )

    def test_short_password_rejection(self):
        """Verify that passwords shorter than 8 characters are rejected with 422."""
        short_passwords = ["", "1", "1234567", "short"]

        for short_pw in short_passwords:
            response = self.client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Short Password User",
                    "email": "valid.user@spectrace.dev",
                    "password": short_pw,
                },
            )
            self.assertEqual(
                response.status_code,
                422,
                f"Expected 422 for password of length {len(short_pw)}, got {response.status_code}",
            )

    def test_response_does_not_contain_password_or_hash(self):
        """Verify that neither plain password nor password hash is returned in response."""
        test_email = f"reg.safe.{uuid.uuid4().hex[:8]}@spectrace.dev"
        self.created_emails.append(test_email)
        raw_password = "SecretPassword!123"

        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Privacy Conscious User",
                "email": test_email,
                "password": raw_password,
            },
        )
        self.assertEqual(response.status_code, 201)
        res_text = response.text
        res_json = response.json()

        # Assert no password fields in JSON structure
        self.assertNotIn("password", res_json)
        self.assertNotIn("hashed_password", res_json)

        # Assert raw password does not appear anywhere in response text
        self.assertNotIn(raw_password, res_text)
        # Assert argon2 signature does not appear in response text
        self.assertNotIn("$argon2id$", res_text)

    def test_existing_test_user_intact(self):
        """Verify that the existing seed test user record is completely unmodified."""
        with SessionLocal() as db:
            seed_user = db.scalar(
                select(User).where(User.email == "test.developer@spectrace.dev")
            )
            self.assertIsNotNone(seed_user)
            self.assertEqual(seed_user.name, "Test Developer")
            self.assertEqual(
                seed_user.hashed_password,
                "mock_pbkdf2_sha256$test_dev_hash_not_a_real_secret",
            )


if __name__ == "__main__":
    unittest.main()
