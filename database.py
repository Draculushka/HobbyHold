from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# В Docker окружение передается через env_file или environment,
# поэтому load_dotenv() здесь не обязателен, если запуск идет в контейнере.
# Но мы оставим его для совместимости, если он найдет файл.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

# Если DATABASE_URL все еще не задан, используем дефолт (только для локальных тестов)
if not DATABASE_URL:
    DATABASE_URL = "postgresql://draculushka:secure_password@db/hobbyheaven"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
