import logging
import time
import uuid
from datetime import datetime

from fastapi import Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def comprehensive_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    logger.info(
        f"[{request_id}] ➡️  {request.method} {request.url.path} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    if request.headers.get("Authorization"):
        logger.info(f"[{request_id}] 🔐 Auth token отримано")

    logger.debug(f"[{request_id}] Origin: {request.headers.get('origin')}")

    start_time = time.perf_counter() 

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"[{request_id}] ❌ Помилка: {str(e)}")
        return JSONResponse(
            content={"error": "Internal server error"},
            status_code=500,
            headers={"X-Request-ID": request_id},
        )

    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
    response.headers["X-Request-ID"] = request_id
    response.headers["X-App-Version"] = "1.0.0"
    response.headers["X-Powered-By"] = "FastAPI"
    response.headers["X-Processed-At"] = datetime.utcnow().isoformat()
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    logger.info(
        f"[{request_id}] ⬅️  Статус: {response.status_code} | "
        f"Час: {process_time * 1000:.2f}ms"
    )

    if process_time > 0.5:
        logger.warning(
            f"[{request_id}] 🐢 SLOW {request.method} {request.url.path} "
            f"[{process_time * 1000:.2f}ms]"
        )

    return response