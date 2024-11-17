from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from loguru import logger

from src.services.company_service import update_company_data_for_all
from src.utils.unitofwork import UnitOfWork

scheduler_app = AsyncIOScheduler()


async def update_outdated_companies():
    async with UnitOfWork() as uow:
        await update_company_data_for_all(uow)



def configure_scheduler():
    """
    Configure the scheduler by adding jobs.
    """
    scheduler_app.add_job(update_outdated_companies, 'interval', minutes=5)
    return scheduler_app


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Asynchronous context manager for managing application lifespan.

    Args:
        _app: The FastAPI application instance.
    """
    logger.info("Starting app...")
    scheduler_app.start()
    yield
    scheduler_app.shutdown()
    logger.info("Scheduler stopped.")

