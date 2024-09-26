from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(String, primary_key=True)
    publication_name = Column(String, nullable=False)
    edition = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    total_pages = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)

    pages = relationship("Page", back_populates="pdf")