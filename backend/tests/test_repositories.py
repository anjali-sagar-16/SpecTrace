"""Automated integration tests for Repository CRUD APIs."""

import unittest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


class TestRepositoryCRUDAPI(unittest.TestCase):
    """Test suite covering /api/v1/projects/{project_id}/repositories CRUD endpoints."""

    @classmethod
    def setUpClass(cls):
        """Create test client and two isolated test users with projects and tokens."""
        cls.client = TestClient(app)

        # 1. User Alpha setup
        cls.user_a_email = f"repo.user.a.{uuid.uuid4().hex[:8]}@spectrace.dev"
        cls.user_a_password = "PasswordA#2026!"
        res_a = cls.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Repo User Alpha",
                "email": cls.user_a_email,
                "password": cls.user_a_password,
            },
        )
        assert res_a.status_code == 201
        cls.user_a_id = res_a.json()["id"]

        login_a = cls.client.post(
            "/api/v1/auth/login",
            json={"email": cls.user_a_email, "password": cls.user_a_password},
        )
        assert login_a.status_code == 200
        cls.token_a = login_a.json()["access_token"]
        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}

        # User Alpha creates Project A1 and Project A2
        proj_a1 = cls.client.post(
            "/api/v1/projects",
            headers=cls.headers_a,
            json={"name": "Alpha Project 1", "description": "Primary Project"},
        )
        assert proj_a1.status_code == 201
        cls.project_a1_id = proj_a1.json()["id"]

        proj_a2 = cls.client.post(
            "/api/v1/projects",
            headers=cls.headers_a,
            json={"name": "Alpha Project 2", "description": "Secondary Project"},
        )
        assert proj_a2.status_code == 201
        cls.project_a2_id = proj_a2.json()["id"]

        # 2. User Beta setup (for cross-user isolation tests)
        cls.user_b_email = f"repo.user.b.{uuid.uuid4().hex[:8]}@spectrace.dev"
        cls.user_b_password = "PasswordB#2026!"
        res_b = cls.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Repo User Beta",
                "email": cls.user_b_email,
                "password": cls.user_b_password,
            },
        )
        assert res_b.status_code == 201
        cls.user_b_id = res_b.json()["id"]

        login_b = cls.client.post(
            "/api/v1/auth/login",
            json={"email": cls.user_b_email, "password": cls.user_b_password},
        )
        assert login_b.status_code == 200
        cls.token_b = login_b.json()["access_token"]
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}

        # User Beta creates Project B
        proj_b = cls.client.post(
            "/api/v1/projects",
            headers=cls.headers_b,
            json={"name": "Beta Project", "description": "User B Project"},
        )
        assert proj_b.status_code == 201
        cls.project_b_id = proj_b.json()["id"]

    @classmethod
    def tearDownClass(cls):
        """Clean up test users and their cascaded projects/repositories."""
        with SessionLocal() as db:
            db.execute(
                delete(User).where(
                    User.email.in_([cls.user_a_email, cls.user_b_email])
                )
            )
            db.commit()

    def test_unauthenticated_requests_rejected(self):
        """Verify unauthenticated requests to repository endpoints return 401."""
        endpoints = [
            ("POST", f"/api/v1/projects/{self.project_a1_id}/repositories", {"name": "Repo", "full_name": "org/repo"}),
            ("GET", f"/api/v1/projects/{self.project_a1_id}/repositories", None),
            ("GET", f"/api/v1/projects/{self.project_a1_id}/repositories/1", None),
            ("DELETE", f"/api/v1/projects/{self.project_a1_id}/repositories/1", None),
        ]

        for method, url, payload in endpoints:
            if method == "POST":
                res = self.client.post(url, json=payload)
            elif method == "GET":
                res = self.client.get(url)
            elif method == "DELETE":
                res = self.client.delete(url)

            self.assertEqual(
                res.status_code,
                401,
                f"Expected 401 for unauthenticated {method} {url}, got {res.status_code}",
            )

    def test_repository_creation_succeeds(self):
        """Verify project owner can add a repository with proper URL-derived project_id."""
        repo_data = {
            "name": "SpecTrace Frontend",
            "full_name": "spectrace-ai/spectrace-frontend",
            "provider": "github",
            "external_id": "987654321",
            "default_branch": "main",
            "html_url": "https://github.com/spectrace-ai/spectrace-frontend",
        }

        res = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json=repo_data,
        )

        self.assertEqual(res.status_code, 201)
        data = res.json()

        self.assertIn("id", data)
        self.assertEqual(data["project_id"], self.project_a1_id)
        self.assertEqual(data["name"], "SpecTrace Frontend")
        self.assertEqual(data["full_name"], "spectrace-ai/spectrace-frontend")
        self.assertEqual(data["provider"], "github")
        self.assertEqual(data["external_id"], "987654321")
        self.assertEqual(data["default_branch"], "main")
        self.assertEqual(data["html_url"], "https://github.com/spectrace-ai/spectrace-frontend")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_project_id_in_body_rejected(self):
        """Verify client cannot supply project_id in request body."""
        res = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={
                "name": "Tamper Repo",
                "full_name": "org/tamper",
                "project_id": 99999,
            },
        )
        self.assertEqual(res.status_code, 422)

    def test_repository_listing_returns_only_project_repositories(self):
        """Verify repository listing returns only repositories belonging to the requested project."""
        # Add repo to Project A1
        res1 = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "A1 Repo", "full_name": "org/a1-repo"},
        )
        self.assertEqual(res1.status_code, 201)
        repo_a1_id = res1.json()["id"]

        # Add repo to Project A2
        res2 = self.client.post(
            f"/api/v1/projects/{self.project_a2_id}/repositories",
            headers=self.headers_a,
            json={"name": "A2 Repo", "full_name": "org/a2-repo"},
        )
        self.assertEqual(res2.status_code, 201)
        repo_a2_id = res2.json()["id"]

        # List repositories for Project A1
        list_a1 = self.client.get(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
        ).json()
        a1_ids = [r["id"] for r in list_a1]
        self.assertIn(repo_a1_id, a1_ids)
        self.assertNotIn(repo_a2_id, a1_ids)
        for r in list_a1:
            self.assertEqual(r["project_id"], self.project_a1_id)

        # List repositories for Project A2
        list_a2 = self.client.get(
            f"/api/v1/projects/{self.project_a2_id}/repositories",
            headers=self.headers_a,
        ).json()
        a2_ids = [r["id"] for r in list_a2]
        self.assertIn(repo_a2_id, a2_ids)
        self.assertNotIn(repo_a1_id, a2_ids)
        for r in list_a2:
            self.assertEqual(r["project_id"], self.project_a2_id)

    def test_get_and_delete_owned_repository(self):
        """Verify owner can fetch and delete an owned repository record."""
        # 1. Create repository
        create_res = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "Lifecycle Repo", "full_name": "org/lifecycle-repo"},
        )
        self.assertEqual(create_res.status_code, 201)
        repo_id = create_res.json()["id"]

        # 2. Get repository
        get_res = self.client.get(
            f"/api/v1/projects/{self.project_a1_id}/repositories/{repo_id}",
            headers=self.headers_a,
        )
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], repo_id)
        self.assertEqual(get_res.json()["name"], "Lifecycle Repo")

        # 3. Delete repository
        del_res = self.client.delete(
            f"/api/v1/projects/{self.project_a1_id}/repositories/{repo_id}",
            headers=self.headers_a,
        )
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["message"], "Repository deleted successfully")

        # 4. Subsequent GET returns 404
        post_del = self.client.get(
            f"/api/v1/projects/{self.project_a1_id}/repositories/{repo_id}",
            headers=self.headers_a,
        )
        self.assertEqual(post_del.status_code, 404)

    def test_another_user_project_cannot_be_accessed(self):
        """Verify User A cannot create, list, view, or delete repos in User B's project (404)."""
        # User B creates a repo in Project B
        res_b = self.client.post(
            f"/api/v1/projects/{self.project_b_id}/repositories",
            headers=self.headers_b,
            json={"name": "Beta Private Repo", "full_name": "org/beta-private"},
        )
        self.assertEqual(res_b.status_code, 201)
        repo_b_id = res_b.json()["id"]

        # User A attempts POST on Project B
        post_cross = self.client.post(
            f"/api/v1/projects/{self.project_b_id}/repositories",
            headers=self.headers_a,
            json={"name": "Intruder Repo", "full_name": "org/intruder"},
        )
        self.assertEqual(post_cross.status_code, 404)
        self.assertEqual(post_cross.json().get("detail"), "Project not found")

        # User A attempts GET list on Project B
        list_cross = self.client.get(
            f"/api/v1/projects/{self.project_b_id}/repositories",
            headers=self.headers_a,
        )
        self.assertEqual(list_cross.status_code, 404)
        self.assertEqual(list_cross.json().get("detail"), "Project not found")

        # User A attempts GET single on Project B repo
        get_cross = self.client.get(
            f"/api/v1/projects/{self.project_b_id}/repositories/{repo_b_id}",
            headers=self.headers_a,
        )
        self.assertEqual(get_cross.status_code, 404)
        self.assertEqual(get_cross.json().get("detail"), "Project not found")

        # User A attempts DELETE on Project B repo
        del_cross = self.client.delete(
            f"/api/v1/projects/{self.project_b_id}/repositories/{repo_b_id}",
            headers=self.headers_a,
        )
        self.assertEqual(del_cross.status_code, 404)
        self.assertEqual(del_cross.json().get("detail"), "Project not found")

    def test_wrong_project_url_access_rejected(self):
        """Verify a repo belonging to project 1 cannot be accessed via project 2 URL (404)."""
        # Create repo in Project A1
        res = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "A1 Only Repo", "full_name": "org/a1-only"},
        )
        self.assertEqual(res.status_code, 201)
        repo_id = res.json()["id"]

        # User A tries to access repo_id via Project A2 URL
        get_mismatch = self.client.get(
            f"/api/v1/projects/{self.project_a2_id}/repositories/{repo_id}",
            headers=self.headers_a,
        )
        self.assertEqual(get_mismatch.status_code, 404)
        self.assertEqual(get_mismatch.json().get("detail"), "Repository not found")

        # User A tries to delete repo_id via Project A2 URL
        del_mismatch = self.client.delete(
            f"/api/v1/projects/{self.project_a2_id}/repositories/{repo_id}",
            headers=self.headers_a,
        )
        self.assertEqual(del_mismatch.status_code, 404)
        self.assertEqual(del_mismatch.json().get("detail"), "Repository not found")

    def test_invalid_input_rejected(self):
        """Verify invalid repository payloads return 422 Unprocessable Entity."""
        # Empty name
        res1 = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "", "full_name": "org/repo"},
        )
        self.assertEqual(res1.status_code, 422)

        # Whitespace-only name
        res2 = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "    ", "full_name": "org/repo"},
        )
        self.assertEqual(res2.status_code, 422)

        # Empty full_name
        res3 = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "valid-name", "full_name": ""},
        )
        self.assertEqual(res3.status_code, 422)

        # Whitespace full_name
        res4 = self.client.post(
            f"/api/v1/projects/{self.project_a1_id}/repositories",
            headers=self.headers_a,
            json={"name": "valid-name", "full_name": "   "},
        )
        self.assertEqual(res4.status_code, 422)


if __name__ == "__main__":
    unittest.main()
