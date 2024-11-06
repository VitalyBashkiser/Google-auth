from src.api.auth import router as router_auth
from src.api.users import router as router_users


all_routers = [
    router_auth,
    router_users,
]
