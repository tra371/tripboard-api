from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import get_settings
from routers.trips import router as trip_router

settings = get_settings()

app = FastAPI()

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

app.include_router(trip_router)


@app.get("/")
async def read_root():
    return {"message": "hello world"}


if __name__ == "__main__":
    import uvicorn

    print(f"port: {type(settings.port)}")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)
