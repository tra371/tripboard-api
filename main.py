from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import get_settings
from routers.api_v1 import api_v1_router

settings = get_settings()

app = FastAPI(
    title="TripBoard API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api")

app.openapi_tags = [
    {"name": "trips", "description": "Trip management"},
    {"name": "calendars", "description": "Trip calendars"},
    {"name": "activities", "description": "Trip activities"},
    {"name": "participants", "description": "Trip participants"},
]


@app.get("/")
async def read_root():
    return {"message": "hello world"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)
