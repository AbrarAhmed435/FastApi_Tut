from fastapi import FastAPI
from routes import router as api_router
from database.connections import engine,Base
from core.middleware import LoggingMiddleware
from contextlib import asynccontextmanager
# from models import Base

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

# include all routes dynamically
app.include_router(api_router)
