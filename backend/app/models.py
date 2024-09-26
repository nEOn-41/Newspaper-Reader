from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
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

class Page(Base):
    __tablename__ = "pages"

    id = Column(String, primary_key=True)
    pdf_id = Column(String, ForeignKey("pdfs.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String, nullable=False)

    pdf = relationship("PDF", back_populates="pages")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    keywords = Column(JSON)
    details = Column(String)

class SystemPrompt(Base):
    __tablename__ = "system_prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String)
    additional_query = Column(String)