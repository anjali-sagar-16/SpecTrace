"""Focused tests for Argon2 password hashing and verification."""

import unittest
from app.core.security import hash_password, verify_password


class TestPasswordSecurity(unittest.TestCase):
    """Test suite covering password hashing, verification, and validation."""

    def test_hash_produces_value_different_from_original(self):
        """Verify hashing produces a distinct Argon2 hash different from plain text."""
        plain = "SpecTrace2026!SecureKey"
        hashed = hash_password(plain)

        # Hash must differ from plain text
        self.assertNotEqual(plain, hashed)
        # Hash must use Argon2id format
        self.assertTrue(
            hashed.startswith("$argon2id$"),
            f"Expected Argon2id prefix, got: {hashed[:15]}...",
        )
        # Distinct calls must produce different hashes due to unique salts
        hashed_again = hash_password(plain)
        self.assertNotEqual(hashed, hashed_again)

    def test_correct_password_verification_succeeds(self):
        """Verify that the matching password verifies successfully."""
        plain = "CorrectDeveloperPassword#99"
        hashed = hash_password(plain)

        self.assertTrue(
            verify_password(plain, hashed),
            "Expected verify_password to return True for matching credentials",
        )

    def test_incorrect_password_verification_fails(self):
        """Verify that incorrect or invalid credentials fail verification."""
        plain = "RealPassword!123"
        hashed = hash_password(plain)

        # Wrong password
        self.assertFalse(verify_password("WrongPassword!123", hashed))
        # Case mismatch
        self.assertFalse(verify_password("realpassword!123", hashed))
        # Corrupted / malformed hash
        self.assertFalse(verify_password(plain, "corrupted_hash_format"))
        self.assertFalse(verify_password(plain, "$argon2id$v=19$m=65536,t=3,p=4$fake_salt$fake_hash"))

    def test_empty_password_rejected(self):
        """Verify that empty, blank, or non-string passwords are rejected during hashing."""
        # Empty string
        with self.assertRaises(ValueError):
            hash_password("")

        # Whitespace-only string
        with self.assertRaises(ValueError):
            hash_password("     ")

        # Tab / newline whitespace
        with self.assertRaises(ValueError):
            hash_password("\t\n ")

        # None or non-string
        with self.assertRaises(ValueError):
            hash_password(None)

        # Verification with empty credentials returns False safely
        sample_hash = hash_password("ValidPassword123")
        self.assertFalse(verify_password("", sample_hash))
        self.assertFalse(verify_password("   ", sample_hash))
        self.assertFalse(verify_password("ValidPassword123", ""))
        self.assertFalse(verify_password(None, sample_hash))
        self.assertFalse(verify_password("ValidPassword123", None))


if __name__ == "__main__":
    unittest.main()
