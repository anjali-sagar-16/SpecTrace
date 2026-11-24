"""Database initialization and development seeding utility for SpecTrace."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.base import Base
from app.db.session import SessionLocal, engine
# Ensure all models are imported so they are registered on Base.metadata
from app.models.user import User
from app.models.project import Project
from app.models.repository import Repository


def init_db() -> None:
    """Creates all database tables registered on SQLAlchemy Base.metadata."""
    print("Creating/verifying database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified successfully.")


def seed_test_user() -> User:
    """Inserts a clearly identified development test user to verify table persistence."""
    test_email = "test.developer@spectrace.dev"
    test_name = "Test Developer"
    # Clearly identified non-sensitive development mock hash
    dev_mock_hash = "mock_pbkdf2_sha256$test_dev_hash_not_a_real_secret"

    with SessionLocal() as db:
        existing_user = db.scalar(select(User).where(User.email == test_email))
        if existing_user:
            print(f"Test user already exists: {existing_user}")
            return existing_user

        new_user = User(
            name=test_name,
            email=test_email,
            hashed_password=dev_mock_hash,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Persisted test user successfully: {new_user}")
        return new_user


def seed_test_project(owner: User) -> Project:
    """Inserts a test project linked to the test user to verify the foreign key relationship."""
    test_project_name = "SpecTrace Core Platform"
    test_project_desc = "Central change intelligence ingestion engine and graph analysis coordinator."

    with SessionLocal() as db:
        existing_project = db.scalar(
            select(Project).where(
                Project.owner_id == owner.id,
                Project.name == test_project_name,
            )
        )
        if existing_project:
            print(f"Test project already exists: {existing_project}")
            return existing_project

        new_project = Project(
            name=test_project_name,
            description=test_project_desc,
            owner_id=owner.id,
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        print(f"Persisted test project successfully: {new_project}")
        return new_project


def seed_test_repository(project: Project) -> Repository:
    """Inserts a test repository linked to the test project to verify the foreign key relationship."""
    test_repo_name = "SpecTrace"
    test_repo_full_name = "anjali-sagar-16/SpecTrace"
    test_provider = "github"
    test_external_id = "891042145"
    test_default_branch = "main"
    test_html_url = "https://github.com/anjali-sagar-16/SpecTrace"

    with SessionLocal() as db:
        existing_repo = db.scalar(
            select(Repository).where(
                Repository.project_id == project.id,
                Repository.full_name == test_repo_full_name,
            )
        )
        if existing_repo:
            print(f"Test repository already exists: {existing_repo}")
            return existing_repo

        new_repo = Repository(
            name=test_repo_name,
            full_name=test_repo_full_name,
            provider=test_provider,
            external_id=test_external_id,
            default_branch=test_default_branch,
            html_url=test_html_url,
            project_id=project.id,
        )
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        print(f"Persisted test repository successfully: {new_repo}")
        return new_repo


def verify_relationships(owner_id: int, project_id: int) -> None:
    """Queries user, project, and repository to verify bidirectional relationships across models."""
    with SessionLocal() as db:
        # 1. User -> Projects
        user = db.scalar(
            select(User).options(selectinload(User.projects)).where(User.id == owner_id)
        )
        print(f"\n[Verified User -> Projects] Owner: {user.name} ({user.email})")
        print(f"Total Projects: {len(user.projects)}")

        # 2. Project -> Repositories
        project = db.scalar(
            select(Project)
            .options(selectinload(Project.repositories))
            .where(Project.id == project_id)
        )
        print(f"\n[Verified Project -> Repositories] Project: '{project.name}' (ID: {project.id})")
        print(f"Total Repositories: {len(project.repositories)}")
        for r in project.repositories:
            print(
                f" - Repo ID={r.id}, FullName='{r.full_name}', Provider='{r.provider}', "
                f"Branch='{r.default_branch}', Back-ref Project='{r.project.name}'"
            )


if __name__ == "__main__":
    init_db()
    test_user = seed_test_user()
    test_project = seed_test_project(test_user)
    test_repo = seed_test_repository(test_project)
    print("\n--- Testing Model Relationships ---")
    verify_relationships(test_user.id, test_project.id)
