from contextlib import asynccontextmanager

import app.models
from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.core.midlleware import comprehensive_middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from app.core.redis import connect_redis, disconnect_redis

logger = setup_logging()

# -------------------------
# LIMITER (GLOBAL)
# -------------------------
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    await connect_redis()
    yield
    await disconnect_redis()
    logger.info("Application shutdown")
    


app = FastAPI(lifespan=lifespan)

# -------------------------
# ATTACH LIMITER TO APP
# -------------------------
app.state.limiter = limiter

# -------------------------
# MIDDLEWARES
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

app.middleware("http")(comprehensive_middleware)

# -------------------------
# EXCEPTION HANDLER (IMPORTANT)
# -------------------------
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

# -------------------------
# STATIC FILES
# -------------------------
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

# -------------------------
# ROUTES
# -------------------------
app.include_router(api_router)


@app.get("/")
def root():
    return {"status": "ok"}
