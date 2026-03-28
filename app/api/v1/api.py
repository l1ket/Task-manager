from fastapi import APIRouter

from app.api.v1 import routes_auth, routes_tasks

router = APIRouter()
router.include_router(routes_auth.router)
router.include_router(routes_tasks.router)
