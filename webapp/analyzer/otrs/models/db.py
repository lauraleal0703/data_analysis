from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

engine = create_engine(
    "mariadb+mariadbconnector://datastudio:GYR4nka2nqt*rkv.xpg@172.16.33.8/otrs?charset=utf8mb4",
    poolclass=NullPool
)

Session = scoped_session(sessionmaker(bind=engine))
session = Session()

Base = declarative_base()
