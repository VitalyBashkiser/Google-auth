from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.services.company_service import update_company_data_for_all
from src.utils.unitofwork import UnitOfWork


async def update_outdated_companies():
    async with UnitOfWork() as uow:
        await update_company_data_for_all(uow)


def start_company_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_outdated_companies, 'interval', minutes=30)
    scheduler.start()
