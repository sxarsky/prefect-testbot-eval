#!/usr/bin/env python3
"""
Initialize database tables for new PR features
This script creates any new tables defined in ORM models that don't exist yet
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from prefect.server.database.orm_models import Base

async def init_db():
    """Create all database tables from ORM models"""
    engine = create_async_engine(
        "postgresql+asyncpg://prefect:prefect@postgres:5432/prefect",
        echo=False
    )

    async with engine.begin() as conn:
        # Create all tables defined in ORM models
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("Database tables created successfully")

if __name__ == "__main__":
    asyncio.run(init_db())
