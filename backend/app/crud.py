from sqlalchemy.orm import Session
from . import models, schemas

def get_pdf(db: Session, pdf_id: str):
    return db.query(models.PDF).filter(models.PDF.id == pdf_id).first()

def get_pdfs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PDF).offset(skip).limit(limit).all()

def create_pdf(db: Session, pdf: schemas.PDFCreate):
    db_pdf = models.PDF(**pdf.dict())
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

# Add similar CRUD functions for Page, Client, and SystemPrompt models