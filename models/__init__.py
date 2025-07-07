import asyncio
from .receiver_model import *
from .item_model import *
from typing import AsyncIterator

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


connect_args = {}

engine = None


def init_db(settings):
    global engine

    engine = create_async_engine(
        "sqlite+aiosqlite:///database.db",
        echo=True,
        future=True,
        connect_args=connect_args,
    )

    asyncio.run(create_db_and_tables())


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def close_session():
    global engine
    if engine is None:
        raise Exception("DatabaseSessionManager is not initialized")
    await engine.dispose()