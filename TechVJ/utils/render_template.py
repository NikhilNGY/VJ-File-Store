import jinja2
import logging
import urllib.parse
import aiohttp
from pathlib import Path
from config import LOG_CHANNEL, URL
from TechVJ.bot import StreamBot
from TechVJ.utils.human_readable import humanbytes
from TechVJ.utils.file_properties import get_file_ids
from TechVJ.server.exceptions import InvalidHash

TEMPLATE_DIR = Path("TechVJ/template")
_TEMPLATE_CACHE: dict[str, jinja2.Template] = {}  # cache loaded templates


async def fetch_remote_file_size(url: str) -> int:
    """Fetch file size from headers asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as resp:
            size = resp.headers.get("Content-Length")
            return int(size) if size else 0


def load_template(name: str) -> jinja2.Template:
    """Load template from file and cache it."""
    if name not in _TEMPLATE_CACHE:
        path = TEMPLATE_DIR / name
        content = path.read_text(encoding="utf-8")
        _TEMPLATE_CACHE[name] = jinja2.Template(content)
    return _TEMPLATE_CACHE[name]


async def render_page(message_id: int, secure_hash: str, src: str | None = None) -> str:
    """
    Render the download page for a file given its message ID and secure hash.

    Args:
        message_id (int): Telegram message ID.
        secure_hash (str): Security hash for the file.
        src (str | None): Optional direct URL.

    Returns:
        str: Rendered HTML page.
    """
    
    # Fetch message & file metadata
    message = await StreamBot.get_messages(int(LOG_CHANNEL), int(message_id))
    file_data = await get_file_ids(StreamBot, int(LOG_CHANNEL), int(message_id))
    
    # Validate hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message ID {message_id}")
        raise InvalidHash
    
    # Build URL if not provided
    src = src or urllib.parse.urljoin(
        URL,
        f"{message_id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}"
    )
    
    # Determine template and file size
    tag = file_data.mime_type.split("/")[0].strip()
    template_name = "req.html" if tag in ["video", "audio"] else "dl.html"
    template = load_template(template_name)
    
    file_size = humanbytes(file_data.file_size)
    if tag not in ["video", "audio"]:
        remote_size = await fetch_remote_file_size(src)
        file_size = humanbytes(remote_size)
    
    # Clean file name
    file_name = file_data.file_name.replace("_", " ")
    
    # Render and return
    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
    )
