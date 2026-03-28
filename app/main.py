from fastapi import FastAPI

from app.api.v1 import routes_auth, routes_tasks

app = FastAPI()
app.include_router(routes_auth.router)
app.include_router(routes_tasks.router)


@app.get("/")
async def root():
    from app.api.v1.util.utils import SECRET_KEY
    return {"message": SECRET_KEY}
