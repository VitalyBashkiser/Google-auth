from datetime import datetime, timedelta

from src.exceptions.errors import PageNotFoundError
from src.parsers.company_parser import parse_company
from src.utils.unitofwork import UnitOfWork


async def get_company_data(uow: UnitOfWork, company_code: str, use_cache: bool = True) -> dict:
    """
    Gets company data from a database or parses it from a website.

    Args:
        uow (UnitOfWork): The unit of work instance for database transactions.
        company_code(str): Company code to look up.
        use_cache(bool): If True, checks the cache (database) before parsing.

    Returns:
        dict: Company data.
    """
    async with uow:
        company = await uow.company.find_one_or_none(code=company_code)

        if use_cache and company and company.last_updated > datetime.utcnow() - timedelta(days=1):
            return company

        try:
            company_data = parse_company(company_code)
        except PageNotFoundError as e:
            raise e

        if company:
            await uow.company.update_instance(company, company_data)
        else:
            await uow.company.add_one(company_data)

        return company_data


async def update_company_data_for_all(uow: UnitOfWork) -> None:
    """
    Updates information for all companies whose data is outdated by more than 24 hours.

    Args:
        uow (UnitOfWork): The unit of work instance for database transactions.

    Returns:
        None
    """
    async with uow:
        stale_companies = await uow.company.get_stale_records(threshold=datetime.utcnow() - timedelta(days=1))

        for company in stale_companies:
            updated_data = parse_company(company.code)
            await uow.company.update_instance(company, updated_data)

        await uow.commit()
