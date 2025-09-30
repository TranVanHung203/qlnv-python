import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

DATABASE_URL = settings.sqlalchemy_database_url

# Ensure we use the async aiomysql driver for MySQL
if DATABASE_URL.startswith("mysql+") and "aiomysql" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("mysql+mysqlconnector", "mysql+aiomysql").replace("mysql+pymysql", "mysql+aiomysql")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def init_db():
    # Import models so metadata is registered
    import app.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
