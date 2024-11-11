from loguru import logger

logger.add("app.log", format="{time} {level} {message}", level="INFO")

__all__ = ["logger"]
