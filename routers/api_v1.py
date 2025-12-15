from fastapi import APIRouter

from routers import activities, calendars, participants, trips

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_v1_router.include_router(calendars.router, prefix="/trips", tags=["calendars"])
api_v1_router.include_router(activities.router, prefix="/trips", tags=["activities"])
api_v1_router.include_router(
    participants.router, prefix="/trips", tags=["participants"]
)
