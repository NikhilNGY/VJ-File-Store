import jinja2
import logging
import aiohttp
import urllib.parse
from config import LOG_CHANNEL, URL
from TechVJ.bot import StreamBot
from TechVJ.utils.human_readable import humanbytes
from TechVJ.utils.file_properties import get_file_ids
from TechVJ.server.exceptions import InvalidHash

async def render_page(message_id: int, secure_hash: str, src: str = None) -> str:
    """
    Render a download or media page for a specific Telegram file.
    
    Args:
        message_id (int): The Telegram message ID containing the file.
        secure_hash (str): The first 6 characters of the file's unique ID to validate the link.
        src (str, optional): Optional custom source URL. Defaults to None.
        
    Returns:
        str: Rendered HTML content.
        
    Raises:
        InvalidHash: If the hash doesn't match the file's unique ID.
    """
    # Fetch the message and file properties
    file_msg = await StreamBot.get_messages(int(LOG_CHANNEL), int(message_id))
    file_data = await get_file_ids(StreamBot, int(LOG_CHANNEL), int(message_id))

    # Validate secure hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - actual hash: {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message ID {message_id}")
        raise InvalidHash

    # Construct file URL if not provided
    if not src:
        src = urllib.parse.urljoin(
            URL,
            f"{message_id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}"
        )

    # Determine file type and size
    file_tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)

    # Select HTML template
    if file_tag in ["video", "audio"]:
        template_file = "TechVJ/template/req.html"
    else:
        template_file = "TechVJ/template/dl.html"
        # Fetch real file size from headers for non-video/audio
        async with aiohttp.ClientSession() as session:
            async with session.get(src) as resp:
                content_length = resp.headers.get("Content-Length")
                if content_length:
                    file_size = humanbytes(int(content_length))

    # Load and render template
    with open(template_file, "r", encoding="utf-8") as f:
        template = jinja2.Template(f.read())

    file_name = file_data.file_name.replace("_", " ")

    html = template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
    )

    return html