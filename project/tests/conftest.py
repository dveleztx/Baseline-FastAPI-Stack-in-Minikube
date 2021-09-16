# Imports
import aioredis
import asyncio
import os
import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.testclient import TestClient
# Custom Imports
from example_com.app import create_app
from example_com.config import Settings, get_settings, tome_key_builder
from example_com.data import db_session


def get_settings_override():
    return Settings(testing=1, environment="test", database_url=os.environ.get("DATABASE_URL"))


@pytest.fixture(scope="module")
def test_app():
    # Setup
    app = create_app()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:

        # Testing
        yield test_client

    # Tear down


@pytest.fixture(scope="module")
def test_app_with_db():
    # Setup
    app = create_app()
    app.dependency_overrides[get_settings] = get_settings_override
    redis = aioredis.from_url(url="redis://localhost", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), key_builder=tome_key_builder, prefix="example")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db_session.global_init())
    with TestClient(app) as test_client:

        # Testing
        yield test_client

    # Tear Down
