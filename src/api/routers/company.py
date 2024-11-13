from fastapi import APIRouter, Query

from src.api.dependencies import UOWDep, SessionDep
from src.services.company_service import get_company_data

router = APIRouter(
    prefix="/company",
    tags=["Company"]
)


@router.get("/company/{company_code}")
async def fetch_company_info(uow: UOWDep, company_code: str, use_cache: bool = Query(True)):
    """
    Endpoint for getting company information.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        company_code (str): Company code to search.
        use_cache (bool): If True, checks the database first before parsing.
    Returns:
        dict: Company data.
    """
    return await get_company_data(uow, company_code, use_cache)
