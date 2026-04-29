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

    auth_token = request.headers.get("Authorization")
    if auth_token:
        logger.info(f"[{request_id}] 🔐 Auth token отримано")

    origin = request.headers.get("origin")
    logger.debug(f"[{request_id}] Origin: {origin}")

    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"[{request_id}] ❌ Помилка: {str(e)}")
        return JSONResponse(
            content={"error": "Internal server error"},
            status_code=500,
            headers={"X-Request-ID": request_id}
        )

    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Request-ID"] = request_id
    response.headers["X-App-Version"] = "1.0.0"
    response.headers["X-Powered-By"] = "FastAPI"
    response.headers["X-Processed-At"] = datetime.utcnow().isoformat()
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    logger.info(
        f"[{request_id}] ⬅️  Статус: {response.status_code} | "
        f"Час: {process_time:.4f}s"
    )

    return response
