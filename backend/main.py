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
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Update the UPLOAD_DIR path
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "DATA"
UPLOAD_DIR = DATA_DIR / "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Update the METADATA_FILE path
METADATA_FILE = DATA_DIR / "metadata.json"

# Load existing metadata on startup
def load_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Error decoding metadata file. Starting with empty metadata.")
    return {}

# Save metadata to file
def save_metadata():
    with open(METADATA_FILE, 'w') as f:
        json.dump(extracted_pages, f)

# Load existing metadata on startup
extracted_pages = load_metadata()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    global extracted_pages
    extracted_pages = load_metadata()
    logger.info(f"Loaded metadata: {len(extracted_pages)} PDFs")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Update the pdf_dir path
        pdf_dir = UPLOAD_DIR / pdf_id
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Open the PDF using PyMuPDF
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        # Store extracted pages and metadata
        extracted_pages[pdf_id] = {
            "publication_name": publication_name,
            "edition": edition,
            "date": date,
            "total_pages": len(doc)
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap()
            
            # Convert PyMuPDF pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            image_path = os.path.join(pdf_dir, f"{page_num + 1}.png")
            
            # Save the image as PNG
            img.save(image_path, "PNG")
        
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
    
    # Create the model
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    batch_size = 15
    current_batch = []
    
    for pdf_id, pdf_data in extracted_pages.items():
        total_pages = pdf_data["total_pages"]
        logger.info(f"Processing PDF {pdf_id} with {total_pages} pages")
        
        for page_num in range(total_pages):
            current_batch.append({
                "id": f"{pdf_id}_{page_num+1}",
                "number": page_num+1,
                "pdf_data": pdf_data
            })
            
            if len(current_batch) == batch_size:
                responses.extend(await process_batch(model, current_batch, query))
                current_batch = []
                
                logger.info("Rate limit reached. Waiting for 60 seconds...")
                await asyncio.sleep(60)
    
    # Process any remaining pages in the last batch
    if current_batch:
        responses.extend(await process_batch(model, current_batch, query))
    
    logger.info(f"Query processing complete. Total responses: {len(responses)}")
    return {"responses": responses}

async def process_batch(model, batch, query):
    tasks = []
    for page in batch:
        task = asyncio.create_task(process_page(model, page, page["pdf_data"], query))
        tasks.append(task)
    
    try:
        batch_responses = await asyncio.gather(*tasks)
        logger.info(f"Processed batch of {len(batch)} pages")
        return batch_responses
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        return []

async def process_page(model, page, pdf_data, query):
    try:
        logger.info(f"Processing page {page['id']}")
        
        # Open the image using PIL
        with Image.open(os.path.join(os.path.join(UPLOAD_DIR, page['id'].split('_')[0]), f"{page['number']}.png")) as img:
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
            "page_id": f"{page['id'].split('_')[0]}_{page['number']}",
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": f"{page['id'].split('_')[0]}_{page['number']}",
            "error": str(e)
        }

@app.get("/list-pdfs")
async def list_pdfs():
    global extracted_pages
    pdf_list = []
    updated_extracted_pages = {}
    for pdf_id, pdf_data in extracted_pages.items():
        pdf_dir = UPLOAD_DIR / pdf_id
        if pdf_dir.exists():
            pdf_list.append({
                "pdf_id": pdf_id,
                "publication_name": pdf_data["publication_name"],
                "edition": pdf_data["edition"],
                "date": pdf_data["date"],
                "page_count": pdf_data["total_pages"]
            })
            updated_extracted_pages[pdf_id] = pdf_data
        else:
            logger.warning(f"PDF directory not found for {pdf_id}. Removing from metadata.")

    if len(updated_extracted_pages) != len(extracted_pages):
        extracted_pages = updated_extracted_pages
        save_metadata()
        logger.info(f"Updated metadata: {len(extracted_pages)} PDFs")

    return {"pdfs": pdf_list}

@app.delete("/delete-pdf/{pdf_id}")
async def delete_pdf(pdf_id: str):
    if pdf_id not in extracted_pages:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Remove the PDF directory
    pdf_dir = UPLOAD_DIR / pdf_id
    if pdf_dir.exists():
        shutil.rmtree(pdf_dir)
    
    del extracted_pages[pdf_id]
    
    # Save updated metadata
    save_metadata()
    
    return {"message": f"PDF with id {pdf_id} has been deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
