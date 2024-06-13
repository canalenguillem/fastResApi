from fastapi import FastAPI
from routes.user import user_router
from routes.role import role_router

app = FastAPI()

app.include_router(user_router)
app.include_router(role_router)
