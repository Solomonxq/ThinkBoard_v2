from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.core.midlleware import comprehensive_middleware

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(comprehensive_middleware)
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")
app.include_router(api_router)


@app.get("/")
def root():
    return {"status": "ok"}