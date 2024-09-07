import os
import uuid  # Add this import
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import asyncio
from dotenv import load_dotenv
import tempfile
import fitz  # PyMuPDF
import io
from PIL import Image
from pydantic import BaseModel
import logging
import shutil
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Create upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define a path for storing metadata
METADATA_FILE = os.path.join(UPLOAD_DIR, "metadata.json")

# Load existing metadata on startup
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save metadata to file
def save_metadata():
    with open(METADATA_FILE, 'w') as f:
        json.dump(extracted_pages, f)

# Load existing metadata on startup
extracted_pages = load_metadata()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store extracted pages and metadata
extracted_pages = {}

class QueryRequest(BaseModel):
    query: str

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    publication_name: str = Form(...),
    edition: str = Form(...),
    date: str = Form(...)
):
    logger.info(f"Received file: {file.filename}")
    logger.info(f"Publication Name: {publication_name}")
    logger.info(f"Edition: {edition}")
    logger.info(f"Date: {date}")
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read the uploaded file content
        pdf_content = await file.read()
        
        # Generate a unique identifier for this PDF
        pdf_id = str(uuid.uuid4())
        
        # Create a directory for this PDF
        pdf_dir = os.path.join(UPLOAD_DIR, pdf_id)
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Store extracted pages and metadata
        extracted_pages[pdf_id] = {
            "publication_name": publication_name,
            "edition": edition,
            "date": date,
            "pages": []
        }
        
        # Open the PDF using PyMuPDF
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap()
            
            # Convert PyMuPDF pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            page_id = f"{pdf_id}_{page_num+1}"
            image_path = os.path.join(pdf_dir, f"page_{page_num+1}.png")
            
            # Save the image as PNG
            img.save(image_path, "PNG")
            
            extracted_pages[pdf_id]["pages"].append({
                "id": page_id,
                "path": image_path,
                "number": page_num + 1
            })
        
        doc.close()
        
        # Save metadata after successful upload
        save_metadata()
        
        return {"message": "PDF uploaded and pages extracted successfully", "pdf_id": pdf_id}
    except Exception as e:
        logger.error(f"Error in upload_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

@app.post("/query")
async def query_pdf(request: QueryRequest):
    query = request.query
    responses = []
    
    logger.info(f"Received query: {query}")
    logger.info(f"Number of PDFs to process: {len(extracted_pages)}")
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    for pdf_id, pdf_data in extracted_pages.items():
        pages = pdf_data["pages"]
        logger.info(f"Processing PDF {pdf_id} with {len(pages)} pages")
        for i in range(0, len(pages), 15):
            batch = pages[i:i+15]
            tasks = []
            for page in batch:
                task = asyncio.create_task(process_page(model, page, pdf_data, query))
                tasks.append(task)
            
            try:
                batch_responses = await asyncio.gather(*tasks)
                responses.extend(batch_responses)
                logger.info(f"Processed batch of {len(batch)} pages")
            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
            
            if i + 15 < len(pages):
                logger.info("Rate limit reached. Waiting for 60 seconds...")
                await asyncio.sleep(60)
    
    logger.info(f"Query processing complete. Total responses: {len(responses)}")
    return {"responses": responses}

@app.get("/list-pdfs")
async def list_pdfs():
    pdf_list = []
    for pdf_id, pdf_data in extracted_pages.items():
        pdf_dir = os.path.join(UPLOAD_DIR, pdf_id)
        if os.path.exists(pdf_dir):
            pdf_list.append({
                "pdf_id": pdf_id,
                "publication_name": pdf_data["publication_name"],
                "edition": pdf_data["edition"],
                "date": pdf_data["date"],
                "page_count": len(pdf_data["pages"])
            })
        else:
            # If the directory doesn't exist, remove it from metadata
            del extracted_pages[pdf_id]
    
    # Save updated metadata
    save_metadata()
    
    return {"pdfs": pdf_list}

@app.delete("/delete-pdf/{pdf_id}")
async def delete_pdf(pdf_id: str):
    if pdf_id not in extracted_pages:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Remove the PDF directory
    pdf_dir = os.path.join(UPLOAD_DIR, pdf_id)
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)
    
    del extracted_pages[pdf_id]
    
    # Save updated metadata
    save_metadata()
    
    return {"message": f"PDF with id {pdf_id} has been deleted"}

async def process_page(model, page, pdf_data, query):
    try:
        logger.info(f"Processing page {page['id']}")
        
        # Open the image using PIL
        with Image.open(page["path"]) as img:
            # Convert the image to RGB mode if it's not already
            img = img.convert('RGB')
            
            # Create a byte stream of the image
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

        SYSTEM_PROMPT = """
        You are an AI assistant specialized in analyzing newspaper pages. Your task is to examine the given newspaper page image and respond to queries about its content. Follow these guidelines:

        1. Analyze the provided newspaper page image carefully.
        2. Focus on finding information related to the given KEYWORDS in the query.
        3. Provide concise and relevant responses.
        4. Format your response as a JSON object with the following structure:

        {
          "retrieval": boolean,
          "keywords": [
            {
              "keyword": string,
              "articles": [
                {
                  "headline": string,
                  "summary": string
                }
              ]
            }
          ]
        }

        - Set "retrieval" to true if any relevant information is found for at least one keyword, false otherwise.
        - Only include the "keywords" array if "retrieval" is true.
        - In the "keywords" array, only include keywords for which articles were found.
        - For each keyword with found articles, list all related articles on the page.
        - Provide a brief, informative summary for each article.

        Remember to consider the provided metadata (Publication, Edition, Date, Page) when analyzing the content.
        """

        response = await model.generate_content_async([
            {
                "mime_type": "image/png",
                "data": img_byte_arr
            },
            f"""
            {SYSTEM_PROMPT}
            Publication: {pdf_data['publication_name']}
            Edition: {pdf_data['edition']}
            Date: {pdf_data['date']}
            Page: {page['number']}
            
            Query: {query}
            """
        ])
        
        logger.info(f"Successfully processed page {page['id']}")
        return {
            "page_id": page["id"],
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page["id"],
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
