from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

# PDF Schemas
class PDFBase(BaseModel):
    publication_name: str
    edition: str
    date: datetime.date
    total_pages: int

class PDFCreate(PDFBase):
    pass

class PDF(PDFBase):
    id: str
    upload_date: datetime.datetime

    class Config:
        orm_mode = True

# Page Schemas
class PageBase(BaseModel):
    page_number: int
    image_path: str

class PageCreate(PageBase):
    pdf_id: str

class Page(PageBase):
    id: str
    pdf_id: str

    class Config:
        orm_mode = True

# Client Schemas
class ClientBase(BaseModel):
    name: str
    keywords: List[str]
    details: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int

    class Config:
        orm_mode = True

# SystemPrompt Schemas
class SystemPromptBase(BaseModel):
    prompt: str
    additional_query: Optional[str] = None

class SystemPromptCreate(SystemPromptBase):
    pass

class SystemPrompt(SystemPromptBase):
    id: int

    class Config:
        orm_mode = True

# Query Schemas
class QueryRequest(BaseModel):
    client_id: int
    additional_query: Optional[str] = None

class QueryResponse(BaseModel):
    page_id: str
    first_response: dict
    second_response: Optional[dict] = None

# List Responses
class PDFList(BaseModel):
    pdfs: List[PDF]

class ClientList(BaseModel):
    clients: List[Client]

class QueryResponseList(BaseModel):
    responses: List[QueryResponse]

# Error Response
class ErrorResponse(BaseModel):
    detail: str