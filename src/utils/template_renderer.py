from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import aiofiles

from src.enums.messages import Messages

env = Environment(loader=FileSystemLoader("src/services/templates"))


async def render_message(message: Messages, context: dict = None) -> HTMLResponse:
    """
    Asynchronously renders an HTML message template based on the provided message flag.

    Args:
        message (Messages): The message flag.
        context (dict, optional): Context to pass to the template.

    Returns:
        HTMLResponse: The rendered HTML response.
    """
    template = env.get_template(f"{message.value}.html")

    async with aiofiles.open(template.filename, mode='r', encoding='utf-8') as f:
        template_content = await f.read()

    content = env.from_string(template_content).render(context or {})
    return HTMLResponse(content=content)
