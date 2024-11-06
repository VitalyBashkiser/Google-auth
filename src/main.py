import uvicorn
from fastapi import FastAPI

from src.api.routers import all_routers


app = FastAPI(title="Authorisation via Email")

for router in all_routers:
    app.include_router(router)
