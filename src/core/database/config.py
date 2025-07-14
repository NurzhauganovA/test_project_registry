from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def async_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        database_url,
        echo=True,
        future=True,
    )

    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
