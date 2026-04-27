from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.core.midlleware import comprehensive_middleware

import app.models


logger = setup_logging()

# -------------------------
# LIMITER (GLOBAL)
# -------------------------
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
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