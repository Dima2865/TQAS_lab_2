import os
import asyncio
import urllib.parse

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncpg

# Устанавливаем переменные окружения для тестов ДО импорта приложения
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_student_db"
os.environ["SECRET_KEY"] = "BHmmwDMkJbMscV-nja5w7WdjOurRE5DNmvco2078F3k"

from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

# --- Асинхронные утилиты для управления базой данных ---
async def database_exists(url: str) -> bool:
    """Проверяет, существует ли база данных с указанным именем."""
    clean_url = url.replace('+asyncpg', '')
    parsed = urllib.parse.urlparse(clean_url)
    dbname = parsed.path.lstrip('/')
    # Подключаемся к стандартной базе 'postgres'
    conn = await asyncpg.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database='postgres'
    )
    try:
        result = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", dbname)
        return bool(result)
    finally:
        await conn.close()

async def create_database(url: str):
    """Создаёт базу данных."""
    clean_url = url.replace('+asyncpg', '')
    parsed = urllib.parse.urlparse(clean_url)
    dbname = parsed.path.lstrip('/')
    conn = await asyncpg.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database='postgres'
    )
    try:
        await conn.execute(f'CREATE DATABASE "{dbname}"')
    finally:
        await conn.close()

async def drop_database(url: str):
    """Удаляет базу данных, предварительно завершая все соединения с ней."""
    clean_url = url.replace('+asyncpg', '')
    parsed = urllib.parse.urlparse(clean_url)
    dbname = parsed.path.lstrip('/')
    conn = await asyncpg.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database='postgres'
    )
    try:
        # Завершаем все активные соединения с целевой БД
        await conn.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{dbname}'
        """)
        await conn.execute(f'DROP DATABASE "{dbname}"')
    finally:
        await conn.close()

# --- Фикстуры pytest ---
@pytest.fixture(scope="session")
def event_loop():
    """Создаём event loop на всю сессию тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Создаёт тестовую БД и таблицы перед всеми тестами, удаляет после."""
    if not await database_exists(TEST_DATABASE_URL):
        await create_database(TEST_DATABASE_URL)
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    await drop_database(TEST_DATABASE_URL)

@pytest_asyncio.fixture(scope="session")
async def engine():
    """Один асинхронный движок на всю тестовую сессию."""
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine, setup_database):
    """Сессия для каждого теста с отдельной транзакцией."""
    async with engine.connect() as connection:
        await connection.begin()
        async_session = sessionmaker(
            connection, class_=AsyncSession, expire_on_commit=False
        )
        session = async_session()
        # Переопределяем зависимость get_db на тестовую сессию
        app.dependency_overrides[get_db] = lambda: session
        yield session
        await session.close()
        await connection.rollback()
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client(db_session):
    """Асинхронный HTTP-клиент для тестирования эндпоинтов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac