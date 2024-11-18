import traceback

from fastapi import APIRouter, Query

from src.api.dependencies import UOWDep, UserIDDep
from src.schemas.company import CompanyDataModel
from src.schemas.subscription import SubscriptionResponseModel
from src.services.company_service import get_company_data, subscribe_user_to_company
from src.enums.choose_company import SourceEnum

router = APIRouter(
    prefix="/company",
    tags=["Company"]
)


@router.get("/company/{company_code}", response_model=CompanyDataModel)
async def fetch_company_info(uow: UOWDep,
                             company_code: str,
                             use_cache: bool = Query(True),
                             source: SourceEnum = Query(SourceEnum.YOURCONTROL)
                             ):
    """
    Endpoint for getting company information.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        company_code (str): Company code to search.
        use_cache (bool): If True, checks the database first before parsing.
        source (str): Company code. Defaults to "youcontrol".
    Returns:
        dict: Company data.
    """
    return await get_company_data(uow, company_code, source, use_cache)


@router.post("/subscribe/{company_code}", response_model=SubscriptionResponseModel)
async def subscribe_to_company_updates(
    company_code: str,
    uow: UOWDep,
    current_user_id: UserIDDep
):
    """
    Endpoint for subscribing an authenticated user to company updates.

    After authentication, the user can subscribe to company data updates using the company code.
    All company update notifications will be sent to the email associated with the user's account.

    Args:
        company_code (str): The code of the company the user wants to subscribe to.
        uow (UOWDep): Dependency for managing transactions.
        current_user_id (int): The ID of the authenticated user.

    Returns:
        dict: Subscription confirmation message.
    """
    return await subscribe_user_to_company(uow, company_code, current_user_id)
