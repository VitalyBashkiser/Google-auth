import inspect

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.config.logger import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling exceptions in HTTP requests.

    This middleware intercepts exceptions raised during request processing, logs detailed
    error information, and returns a standardized JSON response when an error occurs.
    """

    async def dispatch(self, request: Request, call_next: callable) -> JSONResponse:
        """
        Handles exceptions raised during request processing.

        This method tries to process the incoming request and handle any exceptions that occur.
        If an exception is raised, it logs the error details, including the file, line number,
        and function where the error occurred, and returns a standardized JSON error response.

        Args:
            request: The incoming HTTP request object.
            call_next: A function that takes the request and returns a response.

        Returns:
            A JSON response with a 500 status code and a message indicating that the server encountered an issue.

        Raises:
            500 Internal Server Error: Logs the exception details and responds with a generic error message.
        """
        try:
            return await call_next(request)
        except Exception as err:
            trace = inspect.trace()[-1]
            # Log the error message along with relevant details
            logger.error(
                f"""
                                Message: {str(err)}
                                File: {trace.filename}
                                Line number: {trace.lineno}
                                Function: {trace.function}
                                """
            )
            # Reraise a custom exception to indicate a problem with the gateway
            return JSONResponse(
                content={"message": "Sorry, we're experiencing some issues"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
