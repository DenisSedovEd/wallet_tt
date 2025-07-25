from fastapi import APIRouter

from api.v1 import router as v1_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(v1_router)
