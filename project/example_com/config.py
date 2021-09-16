# Imports
import asyncio
import hashlib
import logging
import nest_asyncio
import os
from functools import lru_cache
from fastapi_cache import FastAPICache
from pydantic import BaseSettings, AnyUrl
from starlette.requests import Request
from starlette.responses import Response
from typing import Optional
# Custom Imports
from example_com.infrastructure.jwt_token_auth import decode_auth_value
from example_com.infrastructure.redis import check_master_hash

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    """
    Environment-specific configuration for our application

    Attributes:
        environment (str): Defines the environment (i.e. dev, test, prod)
        testing (bool): Defines whether or not we're in test mode
        database_url (AnyUrl): Defines the database URI path
    """

    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)
    database_url: AnyUrl = os.environ.get("DATABASE_URL")


@lru_cache()
def get_settings() -> BaseSettings:
    """
    Get the config settings from set environment variables

    :return: Environment settings
    """
    log.info("Loading config settings from the environment...")
    return Settings()


def tome_key_builder(
        func,
        namespace: Optional[str] = "",
        request: Optional[Request] = None,
        response: Optional[Response] = None,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
):

    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    cache_key = (
            prefix
            + hashlib.md5(f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode('utf-8'))
            .hexdigest()
    )

    if not request.headers.get("authorization"):
        print("Authoriation:", request.headers.get("authorization"))
        return cache_key

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()

    auth_token = request.headers.get("authorization").split()[-1]
    payload = loop.run_until_complete(decode_auth_value(auth_token))
    username = payload.get('username')

    loop.run_until_complete(check_master_hash(username, namespace, auth_token, cache_key))

    return cache_key
