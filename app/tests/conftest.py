import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:0108@localhost:5432/rbac_test_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client):
    async with TestSessionLocal() as session:
        from app.models.role import Role
        from app.models.user import User
        from app.models.user_role import UserRole
        from app.utils.hashing import hash_password
        import uuid

        role = Role(id=uuid.uuid4(), code="ADMIN", name="Admin")
        user = User(
            id=uuid.uuid4(),
            first_name="Admin",
            last_name="User",
            email="admin_fixture@example.com",
            password_hash=hash_password("adminpass123"),
        )
        session.add(role)
        session.add(user)
        await session.flush()

        session.add(UserRole(user_id=user.id, role_id=role.id))
        await session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "admin_fixture@example.com", "password": "adminpass123"
    })
    token = login_resp.json()["access_token"]
    return token