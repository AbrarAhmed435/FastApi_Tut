# db.py
# ==========================================================
# This file sets up the asynchronous PostgreSQL connection
# for our FastAPI project using SQLAlchemy and asyncpg.
# ----------------------------------------------------------
# Responsibilities:
#   1. Load environment variables from .env
#   2. Initialize async database engine
#   3. Configure async session factory
#   4. Define Base class for ORM models
#   5. Provide session dependency for FastAPI routes
# ==========================================================

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ----------------------------------------------------------
# 1️⃣ Load environment variables
# ----------------------------------------------------------
# Loads key-value pairs from a .env file into system environment.
# This allows us to securely keep secrets (DB credentials, tokens)
# outside our source code.
load_dotenv()

# Get database URL from .env (example format below)
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/db_name"
DATABASE_URL = os.getenv("DATABASE_URL")

# ----------------------------------------------------------
# 2️⃣ Create an asynchronous SQLAlchemy engine
# ----------------------------------------------------------
# The engine manages connections to the database.
# Since we use asyncpg, this engine supports async operations.
#   - echo=True   : prints all SQL queries to console (useful for debugging)
#   - future=True : enables SQLAlchemy 2.0 style API
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# ----------------------------------------------------------
# 3️⃣ Create an async session factory
# ----------------------------------------------------------
# Sessions represent “conversations” with the database.
# Each request to our FastAPI app will use its own session.
#   - bind=engine        : connects the session to our database engine
#   - class_=AsyncSession: makes it asynchronous
#   - expire_on_commit=False : objects remain usable after commit
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ----------------------------------------------------------
# 4️⃣ Define base class for ORM models
# ----------------------------------------------------------
# Every ORM model (table) will inherit from this Base class.
# Example:
#   class User(Base):
#       __tablename__ = "users"
#       id = Column(Integer, primary_key=True)
#       name = Column(String)
Base = declarative_base()

# ----------------------------------------------------------
# 5️⃣ FastAPI dependency: Get async database session
# ----------------------------------------------------------
# This function provides a new async DB session for each request.
# It automatically:
#   - Opens a new session before handling the request
#   - Closes the session after the request finishes (gracefully)
#
# Usage in routes:
#   async def get_users(session: AsyncSession = Depends(get_async_session)):
#       result = await session.execute(select(User))
#       return result.scalars().all()
async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
        # 'yield' allows FastAPI to use the session during the request
        # and close it automatically afterward.

# ==========================================================
# ✅ Summary:
# ----------------------------------------------------------
# - create_async_engine → connects to PostgreSQL (async)
# - AsyncSessionLocal   → session factory for DB transactions
# - Base                → used for ORM model definitions
# - get_async_session   → provides session dependency to routes
# ==========================================================
