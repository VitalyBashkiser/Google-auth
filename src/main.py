import uvicorn
from fastapi import FastAPI

from src.api.main_routers import main_router
from src.api.main_handlers import setup_handlers
from src.core.config.app_settings import AppSettings
from src.schedulers.company_scheduler import start_company_scheduler

app = FastAPI(title="Authorisation via Email")

setup_handlers(app)

app.include_router(main_router)

start_company_scheduler()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=AppSettings.HOST,
        port=AppSettings.PORT,
        reload=AppSettings.RELOAD,
    )
