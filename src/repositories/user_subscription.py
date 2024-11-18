from src.models.user_subscription import UserSubscription
from src.utils.repository import SQLAlchemyRepository


class UserSubscriptionRepository(SQLAlchemyRepository):
    """Repository class for managing UserSubscription objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """

    model = UserSubscription
