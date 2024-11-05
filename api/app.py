from fastapi import FastAPI

from apps.auth.api import router as auth_router
from apps.user.api import router as user_router

app = FastAPI(title="homepage-app")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
