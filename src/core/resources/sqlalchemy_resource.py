import typing

from sqlalchemy.ext import asyncio as asa
from sqlalchemy.ext.asyncio import AsyncEngine


async def sqlalchemy_resource(
    sqlalchemy_database_uri: str, **kwargs: typing.Any
) -> AsyncEngine:
    engine = asa.create_async_engine(sqlalchemy_database_uri, **kwargs)
    return engine
