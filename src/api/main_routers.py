from fastapi import APIRouter

from src.api.routers.auth import router as router_auth
from src.api.routers.users import router as router_users
from src.api.routers.admin.permission import router as router_admin
from src.api.routers.admin.protected import router as router_protected


main_router = APIRouter()

all_routers = [
    router_auth,
    router_users,
    router_admin,
    router_protected,
]


for router in all_routers:
    main_router.include_router(router)
