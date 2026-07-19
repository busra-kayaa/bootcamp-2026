from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

# Config ayarlarını önbellekten (cache) çekiyoruz
settings = get_settings()

# 1. Asenkron motoru (engine) oluşturuyoruz
# echo=settings.debug sayesinde geliştirme aşamasında çalıştırılan SQL sorgularını terminalde görebilirsin.
engine = create_async_engine(
    settings.database_url, 
    echo=settings.debug,  
    future=True
)

# 2. Asenkron oturum (session) üreticisi
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Tüm veritabanı tablolarının (models) miras alacağı temel sınıf
Base = declarative_base()

# 4. FastAPI route'larında her istekte yeni bir asenkron bağlantı açıp kapatacak Bağımlılık (Dependency)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()