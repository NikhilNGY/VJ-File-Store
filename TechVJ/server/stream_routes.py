import re
import time
import math
import logging
import secrets
import mimetypes

from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from TechVJ.bot import multi_clients, work_loads, StreamBot
from TechVJ.server.exceptions import FileNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.utils.time_format import get_readable_time
from TechVJ.utils.custom_dl import ByteStreamer
from TechVJ.utils.render_template import render_page
from config import MULTI_CLIENT

routes = web.RouteTableDef()

# Cache for ByteStreamer objects per client
streamer_cache = {}


@routes.get("/", allow_head=True)
async def root_handler(_):
    """Root route: returns server status and bot info."""
    return web.json_response({
        "server_status": "running",
        "uptime": get_readable_time(time.time() - StartTime),
        "telegram_bot": f"@{StreamBot.username}",
        "connected_bots": len(multi_clients),
        "loads": {
            f"bot{c+1}": l
            for c, (_, l) in enumerate(sorted(work_loads.items(), key=lambda x: x[1], reverse=True))
        },
        "version": __version__,
    })


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_handler(request: web.Request):
    """Render HTML page for watching a media file."""
    try:
        file_id, secure_hash = extract_id_and_hash(request)
        html = await render_page(file_id, secure_hash)
        return web.Response(text=html, content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))


@routes.get(r"/{path:\S+}", allow_head=True)
async def media_handler(request: web.Request):
    """Stream media file with proper HTTP Range handling."""
    try:
        file_id, secure_hash = extract_id_and_hash(request)
        return await stream_file(request, file_id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))


def extract_id_and_hash(request: web.Request):
    """Extract file ID and secure hash from request."""
    path = request.match_info["path"]
    match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
    if match:
        return int(match.group(2)), match.group(1)
    else:
        file_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
        secure_hash = request.rel_url.query.get("hash")
        return file_id, secure_hash


async def get_client_connection():
    """Return the fastest client with a cached ByteStreamer."""
    index = min(work_loads, key=work_loads.get)
    client = multi_clients[index]
    if MULTI_CLIENT:
        logging.info(f"Client {index} serving request")

    if client in streamer_cache:
        return streamer_cache[client]

    streamer = ByteStreamer(client)
    streamer_cache[client] = streamer
    return streamer


def parse_range_header(range_header, file_size, request):
    """Parse HTTP Range header for partial content."""
    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1
    if from_bytes < 0 or until_bytes >= file_size or until_bytes < from_bytes:
        raise web.HTTPRequestRangeNotSatisfiable(
            headers={"Content-Range": f"bytes */{file_size}"}
        )
    return from_bytes, until_bytes


def get_mime_and_filename(file_obj):
    """Determine MIME type and filename for response headers."""
    mime_type = file_obj.mime_type
    file_name = file_obj.file_name

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return mime_type, file_name


async def stream_file(request: web.Request, file_id: int, secure_hash: str):
    """Async streaming of media files with Range support."""
    streamer = await get_client_connection()
    file_obj = await streamer.get_file_properties(file_id)

    if file_obj.unique_id[:6] != secure_hash:
        raise InvalidHash

    file_size = file_obj.file_size
    range_header = request.headers.get("Range")
    from_bytes, until_bytes = parse_range_header(range_header, file_size, request)

    chunk_size = 1024 * 1024  # 1 MB
    offset = from_bytes - (from_bytes % chunk_size)
    first_cut = from_bytes - offset
    last_cut = until_bytes % chunk_size + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    mime_type, file_name = get_mime_and_filename(file_obj)
    req_length = until_bytes - from_bytes + 1

    headers = {
        "Content-Type": mime_type,
        "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
        "Content-Length": str(req_length),
        "Content-Disposition": f'attachment; filename="{file_name}"',
        "Accept-Ranges": "bytes",
    }

    resp = web.StreamResponse(status=206 if range_header else 200, headers=headers)
    await resp.prepare(request)

    # Async streaming
    async for chunk in streamer.yield_file_async(
        file_obj, 0, offset, first_cut, last_cut, part_count, chunk_size
    ):
        await resp.write(chunk)

    await resp.write_eof()
    return resp
