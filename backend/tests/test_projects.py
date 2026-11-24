"""Automated integration tests for Project CRUD APIs."""

import unittest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.project import Project
from app.models.repository import Repository
from app.models.user import User


class TestProjectCRUDAPI(unittest.TestCase):
    """Test suite covering /api/v1/projects CRUD endpoints and ownership isolation."""

    @classmethod
    def setUpClass(cls):
        """Create test client and two isolated test users with auth tokens."""
        cls.client = TestClient(app)

        # User A setup
        cls.user_a_email = f"user.a.{uuid.uuid4().hex[:8]}@spectrace.dev"
        cls.user_a_password = "PasswordA#2026!"
        res_a = cls.client.post(
            "/api/v1/auth/register",
            json={
                "name": "User Alpha",
                "email": cls.user_a_email,
                "password": cls.user_a_password,
            },
        )
        assert res_a.status_code == 201, f"User A registration failed: {res_a.text}"
        cls.user_a_id = res_a.json()["id"]

        login_a = cls.client.post(
            "/api/v1/auth/login",
            json={"email": cls.user_a_email, "password": cls.user_a_password},
        )
        assert login_a.status_code == 200
        cls.token_a = login_a.json()["access_token"]
        cls.headers_a = {"Authorization": f"Bearer {cls.token_a}"}

        # User B setup (to test strict cross-user isolation)
        cls.user_b_email = f"user.b.{uuid.uuid4().hex[:8]}@spectrace.dev"
        cls.user_b_password = "PasswordB#2026!"
        res_b = cls.client.post(
            "/api/v1/auth/register",
            json={
                "name": "User Beta",
                "email": cls.user_b_email,
                "password": cls.user_b_password,
            },
        )
        assert res_b.status_code == 201, f"User B registration failed: {res_b.text}"
        cls.user_b_id = res_b.json()["id"]

        login_b = cls.client.post(
            "/api/v1/auth/login",
            json={"email": cls.user_b_email, "password": cls.user_b_password},
        )
        assert login_b.status_code == 200
        cls.token_b = login_b.json()["access_token"]
        cls.headers_b = {"Authorization": f"Bearer {cls.token_b}"}

    @classmethod
    def tearDownClass(cls):
        """Clean up test users and their cascaded projects."""
        with SessionLocal() as db:
            db.execute(
                delete(User).where(
                    User.email.in_([cls.user_a_email, cls.user_b_email])
                )
            )
            db.commit()

    def test_unauthenticated_requests_rejected(self):
        """Verify that all project endpoints reject unauthenticated requests with 401."""
        endpoints = [
            ("POST", "/api/v1/projects", {"name": "No Auth Project"}),
            ("GET", "/api/v1/projects", None),
            ("GET", "/api/v1/projects/99999", None),
            ("PATCH", "/api/v1/projects/99999", {"name": "Updated"}),
            ("DELETE", "/api/v1/projects/99999", None),
        ]

        for method, url, payload in endpoints:
            if method == "POST":
                res = self.client.post(url, json=payload)
            elif method == "GET":
                res = self.client.get(url)
            elif method == "PATCH":
                res = self.client.patch(url, json=payload)
            elif method == "DELETE":
                res = self.client.delete(url)

            self.assertEqual(
                res.status_code,
                401,
                f"Expected 401 for unauthenticated {method} {url}, got {res.status_code}",
            )

    def test_project_creation_succeeds(self):
        """Verify an authenticated user can create a project with correct ownership."""
        project_name = f"Alpha Project {uuid.uuid4().hex[:6]}"
        project_desc = "Core intelligence analysis service"

        res = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": project_name, "description": project_desc},
        )

        self.assertEqual(res.status_code, 201)
        data = res.json()

        self.assertIn("id", data)
        self.assertEqual(data["name"], project_name)
        self.assertEqual(data["description"], project_desc)
        # Verify ownership is set to the authenticated user
        self.assertEqual(data["owner_id"], self.user_a_id)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_owner_id_not_accepted_from_client(self):
        """Verify that client cannot tamper with or supply owner_id."""
        res = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={
                "name": "Tamper Test Project",
                "description": "Attempting to hijack owner_id",
                "owner_id": self.user_b_id,
            },
        )
        # Extra fields forbidden returns 422 Unprocessable Entity
        self.assertEqual(res.status_code, 422)

    def test_project_listing_returns_only_authenticated_user_projects(self):
        """Verify project listing isolates projects strictly per user."""
        # Create project under User A
        res_a = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "User A Exclusive Project"},
        )
        self.assertEqual(res_a.status_code, 201)
        proj_a_id = res_a.json()["id"]

        # Create project under User B
        res_b = self.client.post(
            "/api/v1/projects",
            headers=self.headers_b,
            json={"name": "User B Exclusive Project"},
        )
        self.assertEqual(res_b.status_code, 201)
        proj_b_id = res_b.json()["id"]

        # List projects as User A
        list_a = self.client.get("/api/v1/projects", headers=self.headers_a).json()
        list_a_ids = [p["id"] for p in list_a]
        self.assertIn(proj_a_id, list_a_ids)
        self.assertNotIn(proj_b_id, list_a_ids)
        for p in list_a:
            self.assertEqual(p["owner_id"], self.user_a_id)

        # List projects as User B
        list_b = self.client.get("/api/v1/projects", headers=self.headers_b).json()
        list_b_ids = [p["id"] for p in list_b]
        self.assertIn(proj_b_id, list_b_ids)
        self.assertNotIn(proj_a_id, list_b_ids)
        for p in list_b:
            self.assertEqual(p["owner_id"], self.user_b_id)

    def test_get_owned_project_succeeds(self):
        """Verify owner can fetch project details by ID."""
        create_res = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "Get Test Project", "description": "Fetch test"},
        )
        self.assertEqual(create_res.status_code, 201)
        project_id = create_res.json()["id"]

        res = self.client.get(
            f"/api/v1/projects/{project_id}",
            headers=self.headers_a,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], project_id)
        self.assertEqual(data["name"], "Get Test Project")
        self.assertEqual(data["owner_id"], self.user_a_id)

    def test_update_owned_project_succeeds(self):
        """Verify owner can update name and description, but not owner_id."""
        create_res = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "Initial Name", "description": "Initial Desc"},
        )
        self.assertEqual(create_res.status_code, 201)
        project_id = create_res.json()["id"]

        # Update name and description
        update_res = self.client.patch(
            f"/api/v1/projects/{project_id}",
            headers=self.headers_a,
            json={"name": "Updated Name", "description": "Updated Desc"},
        )
        self.assertEqual(update_res.status_code, 200)
        data = update_res.json()
        self.assertEqual(data["name"], "Updated Name")
        self.assertEqual(data["description"], "Updated Desc")
        self.assertEqual(data["owner_id"], self.user_a_id)

        # Attempt to pass owner_id in patch must fail with 422
        bad_patch = self.client.patch(
            f"/api/v1/projects/{project_id}",
            headers=self.headers_a,
            json={"owner_id": self.user_b_id},
        )
        self.assertEqual(bad_patch.status_code, 422)

    def test_delete_owned_project_succeeds(self):
        """Verify owner can delete their project."""
        create_res = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "Delete Me Project"},
        )
        self.assertEqual(create_res.status_code, 201)
        project_id = create_res.json()["id"]

        del_res = self.client.delete(
            f"/api/v1/projects/{project_id}",
            headers=self.headers_a,
        )
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["message"], "Project deleted successfully")

        # Subsequent GET must return 404
        get_res = self.client.get(
            f"/api/v1/projects/{project_id}",
            headers=self.headers_a,
        )
        self.assertEqual(get_res.status_code, 404)

    def test_accessing_another_user_project_returns_404(self):
        """Verify accessing, updating, or deleting another user's project returns 404."""
        # Create project under User B
        res_b = self.client.post(
            "/api/v1/projects",
            headers=self.headers_b,
            json={"name": "User B Secret Project"},
        )
        self.assertEqual(res_b.status_code, 201)
        project_b_id = res_b.json()["id"]

        # User A attempts GET on User B's project
        get_res = self.client.get(
            f"/api/v1/projects/{project_b_id}",
            headers=self.headers_a,
        )
        self.assertEqual(get_res.status_code, 404)
        self.assertEqual(get_res.json().get("detail"), "Project not found")

        # User A attempts PATCH on User B's project
        patch_res = self.client.patch(
            f"/api/v1/projects/{project_b_id}",
            headers=self.headers_a,
            json={"name": "Hijacked Name"},
        )
        self.assertEqual(patch_res.status_code, 404)
        self.assertEqual(patch_res.json().get("detail"), "Project not found")

        # User A attempts DELETE on User B's project
        delete_res = self.client.delete(
            f"/api/v1/projects/{project_b_id}",
            headers=self.headers_a,
        )
        self.assertEqual(delete_res.status_code, 404)
        self.assertEqual(delete_res.json().get("detail"), "Project not found")

    def test_invalid_project_data_rejected(self):
        """Verify invalid project names (empty, whitespace, too long) are rejected."""
        # Empty string
        res_empty = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": ""},
        )
        self.assertEqual(res_empty.status_code, 422)

        # Whitespace-only string
        res_ws = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "     "},
        )
        self.assertEqual(res_ws.status_code, 422)

        # Name exceeding 150 characters
        res_long = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "A" * 151},
        )
        self.assertEqual(res_long.status_code, 422)

    def test_cascade_delete_repository(self):
        """Verify that deleting a project cascades to delete associated repositories."""
        create_res = self.client.post(
            "/api/v1/projects",
            headers=self.headers_a,
            json={"name": "Cascade Test Project"},
        )
        self.assertEqual(create_res.status_code, 201)
        project_id = create_res.json()["id"]

        # Insert repository attached to this project
        with SessionLocal() as db:
            repo = Repository(
                project_id=project_id,
                name="cascade-test-repo",
                full_name="org/cascade-test-repo",
                provider="github",
            )
            db.add(repo)
            db.commit()
            repo_id = repo.id

        # Delete project via API
        del_res = self.client.delete(
            f"/api/v1/projects/{project_id}",
            headers=self.headers_a,
        )
        self.assertEqual(del_res.status_code, 200)

        # Verify repository is gone from database
        with SessionLocal() as db:
            persisted_repo = db.scalar(
                select(Repository).where(Repository.id == repo_id)
            )
            self.assertIsNone(persisted_repo)


if __name__ == "__main__":
    unittest.main()
