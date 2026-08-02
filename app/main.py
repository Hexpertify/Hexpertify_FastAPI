from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.router import api_router
from app.middleware.exception_handler import register_exception_handlers

app = FastAPI(title="RBAC API")

register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"status": "ok", "db": result.scalar() == 1}