from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(String, primary_key=True)
    pdf_id = Column(String, ForeignKey("pdfs.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String, nullable=False)

    pdf = relationship("PDF", back_populates="pages")