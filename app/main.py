from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import home, user, dashboard, category, product

from app.core.exceptions import LoginRequiredException
from app.core.handlers import login_required_exception_handler

app = FastAPI(title="Inventory Management System")
app.add_exception_handler(
    LoginRequiredException,
    login_required_exception_handler,
)
app.add_middleware(SessionMiddleware, secret_key="this-is-a-secret-key")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router)
app.include_router(user.router)
app.include_router(dashboard.router)
app.include_router(category.router)
app.include_router(product.router)
