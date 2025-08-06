import typing

from sqlalchemy.ext import asyncio as asa
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.logger import logger


async def sqlalchemy_resource(
    sqlalchemy_database_uri: str, **kwargs: typing.Any
) -> AsyncEngine:
    try:
        engine = asa.create_async_engine(sqlalchemy_database_uri, **kwargs)
        async with engine.connect():
            pass

        return engine

    except Exception as err:
        logger.critical(f"Error creating database engine: {err}", exc_info=True)
        raise
