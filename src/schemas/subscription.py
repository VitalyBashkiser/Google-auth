from datetime import datetime

from pydantic import BaseModel


class SubscriptionResponseModel(BaseModel):
    user_id: int
    company_id: int
    created_at: datetime
