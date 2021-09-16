# Imports
import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
# Custom Imports
from example_com.data.modelbase import SqlAlchemyBase

__async_engine: Optional[AsyncEngine] = None
DATABASE_URL: Optional[str] = None


async def global_init():
    global __async_engine

    async_conn_str = os.environ.get("DATABASE_URL")
    __async_engine = create_async_engine(async_conn_str, echo=False)

    # noinspection PyUnresolvedReferences
    import example_com.data.__all_models

    # Create Tables from the Models
    async with __async_engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)


def create_session() -> AsyncSession:
    global __async_engine

    if not __async_engine:
        raise Exception("You must call global_init() before using this method")

    session: AsyncSession = AsyncSession(__async_engine)
    session.sync_session.expire_on_commit = False

    return session

