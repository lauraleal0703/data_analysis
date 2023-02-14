from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql://datastudio:GYR4nka2nqt*rkv.xpg@172.16.33.8/otrs?charset=utf8mb4",
    pool_size=50,
    max_overflow=1000
)
Session = sessionmaker(bind=engine, autoflush=True)
session = Session()

Base = declarative_base()