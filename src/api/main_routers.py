from fastapi import APIRouter

from src.api.routers.auth import router as router_auth
from src.api.routers.users import router as router_users


main_router = APIRouter()

all_routers = [
    router_auth,
    router_users,
]


for router in all_routers:
    main_router.include_router(router)
