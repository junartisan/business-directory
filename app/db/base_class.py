from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    # This makes it so you don't have to manually type __tablename__ 
    # for every single model if you don't want to.
    pass