"""
Main API router for version 1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, patients, encounters, users, sync, abdm

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(encounters.router, prefix="/encounters", tags=["encounters"])
api_router.include_router(sync.router, prefix="/sync", tags=["synchronization"])
api_router.include_router(abdm.router, prefix="/abdm", tags=["abdm"]) 