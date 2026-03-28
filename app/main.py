from fastapi import FastAPI

from app.api.v1.api import router as api_router
from app.core.models import HealthResponse

app = FastAPI(title="Task Manager API")
app.include_router(api_router)


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse()
