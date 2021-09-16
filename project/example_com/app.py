#!/usr/bin/python3
###############################################################################
# Script      : app.py
# Author      : David Velez
# Date        : 09/15/2021
# Description : Template API
###############################################################################

# Imports
import aioredis
import json
import logging
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from pathlib import Path
# Custom Imports
from example_com.config import tome_key_builder
from example_com.data import db_session
from example_com.api.admin import admin_api
from example_com.api.account import accounts_api
from example_com.api.workspaces import projects_api
from example_com.infrastructure import jwt_token_auth

log = logging.getLogger("uvicorn")


def create_app() -> FastAPI:
    api = FastAPI()
    configure_settings()
    configure_routers(api)

    return api


def configure_settings():
    file = Path("./example_com/settings.json").absolute()
    if not file.exists():
        print(f"WARNING: {file} file not found, you cannot continue, please see settings_template.json")
        raise FileExistsError("settings.json file not found you cannot continue, please see settings_template.json")

    with open("./example_com/settings.json") as fin:
        settings = json.load(fin)
        jwt_token_auth.JWT_SECRET = settings.get("jwt_secret")
        db_session.DATABASE_URL = settings.get("database_url")


def configure_routers(api):
    api.include_router(admin_api.router, tags=["admin"])
    api.include_router(accounts_api.router, tags=["accounts"])
    api.include_router(projects_api.router, tags=["projects"])


app = create_app()


async def setup_db():
    await db_session.global_init()


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(url="redis://localhost", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), key_builder=tome_key_builder, prefix="example")
    await setup_db()
