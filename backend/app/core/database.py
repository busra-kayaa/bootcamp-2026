from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

# Config ayarlarını önbellekten (cache) çekiyoruz
settings = get_settings()

# 1. Asenkron motoru (engine) oluşturuyoruz
engine = create_async_engine(
    settings.database_url, 
    echo=settings.debug,  
    future=True,
    # --- YENİ EKLENEN GÜÇLENDİRİCİ AYARLAR ---
    pool_pre_ping=True,  # İşlem yapmadan önce PostgreSQL'e "Orada mısın?" diye sorar, koptuysa yeni bağlantı açar.
    pool_recycle=1800,   # 30 dakikada bir bağlantıları temizleyip tazeler.
    connect_args={
        "command_timeout": 1200  # AI vektör işlemleri uzun sürerse veritabanının 20 dakika sabretmesini sağlar.
    }
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