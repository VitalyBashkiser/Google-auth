import uvicorn
from fastapi import FastAPI

from src.api.main_routers import main_router
from src.api.main_handlers import setup_handlers

app = FastAPI(title="Authorisation via Email")

setup_handlers(app)

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
    )
