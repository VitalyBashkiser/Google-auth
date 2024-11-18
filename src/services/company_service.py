from datetime import datetime, timedelta

from loguru import logger
from starlette.responses import HTMLResponse

from src.enums.messages import Messages
from src.exceptions.errors import CompanyNotFoundError, AlreadySubscribedError
from src.notifications.notifier import notify_user
from src.parsers.company_parser import parse_company
from src.schemas.company import CompanyDataModel
from src.utils.template_renderer import render_message
from src.utils.unitofwork import UnitOfWork


async def fetch_or_update_company(uow: UnitOfWork,
                                  company_code: str,
                                  source: str = "youcontrol",
                                  company_data: CompanyDataModel | None = None
                                  ) -> CompanyDataModel:
    """
    Fetches company data from a parser or updates it in the database.

    Args:
        uow (UnitOfWork): The unit of work instance for database transactions.
        company_code (str): The company code to look up or update.
        source (str): The source of the company data.
        company_data (CompanyDataModel | None): Existing company data from the database.

    Returns:
        CompanyDataModel: The updated or fetched company data.
    """
    async with uow:
        parsed_data = parse_company(company_code, source=source)

        logger.info(f"Parsed data: {parsed_data}")
        parsed_data_model = CompanyDataModel(**parsed_data)
        logger.info(f"Model created: {parsed_data_model}")

        if company_data:
            if parsed_data_model.dict(exclude={"id"}) != company_data.dict(exclude={"id"}):
                await uow.company.update_one(company_data.id, parsed_data_model.dict(exclude={"id"}))
                logger.info(f"Company {company_code} is updated successfully.")
        else:
            new_id = await uow.company.add_one(parsed_data_model.dict(exclude={"id"}))
            parsed_data_model.id = new_id
            logger.info(f"Company {company_code} is added successfully.")

        await uow.commit()
        return parsed_data_model


async def get_company_data(uow: UnitOfWork, company_code: str, source: str = "youcontrol", use_cache: bool = True) -> dict:
    """
    Gets company data from a database or parses it from a website.

    Args:
        uow (UnitOfWork): The unit of work instance for database transactions.
        company_code(str): Company code to look up.
        source (str): The source of the company data.
        use_cache(bool): If True, checks the cache (database) before parsing.

    Returns:
        dict: Company data.
    """
    async with uow:
        company = await uow.company.find_one_or_none(code=company_code)

        if use_cache and company and company.last_updated > datetime.utcnow() - timedelta(days=1):
            return CompanyDataModel.from_orm(company).dict()

        return await fetch_or_update_company(uow, company_code, source, CompanyDataModel.from_orm(company) if company else None)


async def update_company_data_for_all(uow: UnitOfWork, source: str = "youcontrol") -> None:
    """
    Updates information for all companies whose data is outdated by more than 24 hours.

    Args:
        uow (UnitOfWork): The unit of work instance for database transactions.
        source (str): The source of the company data.

    Returns:
        None
    """
    async with uow:
        stale_companies = await uow.company.get_stale_records_as_dict(
            threshold=datetime.utcnow() - timedelta(days=1)
        )
        logger.info(f"Find {len(stale_companies)} outdated companies to update")

        for company_data in stale_companies:
            company_model = CompanyDataModel(**company_data)
            updated_data = CompanyDataModel(**parse_company(company_model.code, source=source))

            if updated_data.dict(exclude={"id"}) != company_model.dict(exclude={"id"}):
                await uow.company.update_one(company_model.id, updated_data.dict(exclude={"id"}))
                logger.info(f"Company {company_model.code} is updated")

        await uow.commit()
        logger.info("All obsolete companies have been updated")


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
        company_name = company.name
        await uow.commit()

        return {"message": f"You are now subscribed to updates for company {company_name}"}


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
            if isinstance(message_content, HTMLResponse):
                message_content = message_content.body.decode("utf-8")
            await notify_user(user.email, "Company Update Notification", message_content)
