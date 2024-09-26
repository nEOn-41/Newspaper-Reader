from sqlalchemy import Column, Integer, String, JSON
from .base import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    keywords = Column(JSON)
    details = Column(String)