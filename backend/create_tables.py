"""Create all database tables from SQLAlchemy models.

Usage: python create_tables.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base

# Import all models so they register with Base.metadata
from app.models.doctor import Doctor  # noqa: F401
from app.models.conversation import Conversation, Appointment  # noqa: F401
from app.models.campaign import Campaign  # noqa: F401
from app.models.call_log import CallLog, ConversionEvent  # noqa: F401
from app.models.billing import Subscription, Invoice  # noqa: F401
from app.models.clinic_staff import ClinicStaff  # noqa: F401
from app.models.patient import Patient  # noqa: F401


async def create_all():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()
    print("\n✓ All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_all())
