import traceback
from datetime import datetime, timedelta

from loguru import logger
from deepdiff import DeepDiff

from src.enums.messages import Messages
from src.exceptions.errors import PageNotFoundError, CompanyNotFoundError, AlreadySubscribedError
from src.notifications.notifier import notify_user
from src.parsers.company_parser import parse_company
from src.utils.template_renderer import render_message
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
        logger.info(f"Find {len(stale_companies)} old data companies for updates")

        for company in stale_companies:
            updated_data = parse_company(company.code)
            current_data = company.to_dict()

            differences = DeepDiff(current_data, updated_data, ignore_order=True)

            if differences:
                logger.info(f"Updating data for company {company.name} ({company.code})")
                logger.debug(f"Differences found: {differences}")

                await uow.company.update_instance(company, updated_data)

                await notify_subscribers_of_update(company.id, uow)

                await uow.commit()
            else:
                logger.info(f"No updates for company {company.name} ({company.code})")


async def subscribe_user_to_company(uow: UnitOfWork, company_code: str, user_id: int) -> dict:
    """
    Subscribes a user to company updates by company code.

    This function checks if the company exists and if the user is already subscribed to its updates.

    If the company is found and there is no subscription, it is added to the database.

    Args:
        uow(UnitOfWork): UnitOfWork instance for managing transactions.
        company_code(str): The code of the company the user wants to subscribe to.
        user_id(int): The authenticated user who is subscribing to the company.

    Returns:
        dict: Confirmation of successful subscription to company updates.
    """
    async with uow:
        company = await uow.company.find_one_or_none(code=company_code)
        if not company:
            raise CompanyNotFoundError

        subscription_exists = await uow.user_subscription.subscription_exists(user_id, company.id)
        if subscription_exists:
            raise AlreadySubscribedError(model_name="UserSubscription", id_=user_id)

        await uow.user_subscription.add_subscription(user_id, company.id)
        await uow.commit()

        return {"message": f"You are now subscribed to updates for company {company.name}"}


async def notify_subscribers_of_update(company_id: int, uow: UnitOfWork):
    """
    Notify subscribers about a company update.

    Args:
        company_id (int): ID of the company for which the update occurred.
        uow (UnitOfWork): Unit of Work instance for database transactions.
    """
    async with uow:
        company = await uow.company.find_one_or_none(id=company_id)
        if not company:
            return

        subscribers = await uow.user_subscription.get_users_subscribed_to_company(company_id)

        for user in subscribers:
            context = {
                "username": user.email,
                "company_name": company.name,
            }
            message_content = await render_message(Messages.COMPANY_UPDATE_NOTIFICATION, context)
            await notify_user(user.email, "Company Update Notification", message_content)
