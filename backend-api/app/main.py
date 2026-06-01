from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.seed import seed_defaults
from app.db.session import SessionLocal, init_db

configure_logging()

app = FastAPI(title="LithiumCraft API", version="0.1.0", description="锂电池制造工艺知识库 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def startup() -> None:
    init_db()
    with SessionLocal() as db:
        seed_defaults(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "lithiumcraft-api"}
