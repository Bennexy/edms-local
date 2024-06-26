import sys

sys.path.append(".")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as DB
from sqlalchemy.ext.declarative import declarative_base

from api import config

Base = declarative_base()


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=create_engine(config.DATABASE_URI)
)


def db(func):
    def wrapper(*args, **kwargs):
        try:
            close = False
            if "db" in kwargs and not isinstance(kwargs["db"], DB):
                raise Exception(
                    f"Invalid argument db type passed to {func.__name__} required type: sqlalchemy.orm.session.Session - passed type: {type(kwargs['db']).__name__}"
                )

            else:
                kwargs["db"] = db = SessionLocal()
                close = True

            return func(*args, **kwargs)
        finally:
            try:
                if close:
                    db.close()
            except Exception:
                pass

    return wrapper
