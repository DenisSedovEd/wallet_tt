from fastapi import APIRouter

from api.v1.wallets.views import router as wallet_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(wallet_router)
