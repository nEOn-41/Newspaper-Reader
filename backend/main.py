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

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    publication_name: str = Form(...),
    edition: str = Form(...),
    date: str = Form(...)
):
    print(f"Received file: {file.filename}")
    print(f"Publication Name: {publication_name}")
    print(f"Edition: {edition}")
    print(f"Date: {date}")
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read the uploaded file content
        pdf_content = await file.read()
        
        # Generate a unique identifier for this PDF
        pdf_id = str(uuid.uuid4())
        
        # Create a temporary directory for storing images
        with tempfile.TemporaryDirectory() as temp_dir:
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
                image_path = os.path.join(temp_dir, f"{page_id}.png")
                
                # Save the image as PNG
                img.save(image_path, "PNG")
                
                extracted_pages[pdf_id]["pages"].append({
                    "id": page_id,
                    "path": image_path,
                    "number": page_num + 1
                })
            
            doc.close()
        
        return {"message": "PDF uploaded and pages extracted successfully", "pdf_id": pdf_id}
    except Exception as e:
        print(f"Error in upload_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

@app.post("/query")
async def query_pdf(pdf_id: str, query: str):
    if pdf_id not in extracted_pages:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_data = extracted_pages[pdf_id]
    pages = pdf_data["pages"]
    responses = []
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    for i in range(0, len(pages), 15):
        batch = pages[i:i+15]
        tasks = []
        for page in batch:
            task = asyncio.create_task(process_page(model, page, pdf_data, query))
            tasks.append(task)
        
        batch_responses = await asyncio.gather(*tasks)
        responses.extend(batch_responses)
        
        if i + 15 < len(pages):
            print("Rate limit reached. Waiting for 60 seconds...")
            await asyncio.sleep(60)
    
    return {"responses": responses}

@app.get("/list-pdfs")
async def list_pdfs():
    pdf_list = []
    for pdf_id, pdf_data in extracted_pages.items():
        pdf_list.append({
            "pdf_id": pdf_id,
            "publication_name": pdf_data["publication_name"],
            "edition": pdf_data["edition"],
            "date": pdf_data["date"],
            "page_count": len(pdf_data["pages"])
        })
    return {"pdfs": pdf_list}

@app.delete("/delete-pdf/{pdf_id}")
async def delete_pdf(pdf_id: str):
    if pdf_id not in extracted_pages:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    del extracted_pages[pdf_id]
    return {"message": f"PDF with id {pdf_id} has been deleted"}

async def process_page(model, page, pdf_data, query):
    try:
        with open(page["path"], "rb") as image_file:
            image_data = image_file.read()
        
        response = await model.generate_content_async([
            image_data,
            f"""
            Publication: {pdf_data['publication_name']}
            Edition: {pdf_data['edition']}
            Date: {pdf_data['date']}
            Page: {page['number']}
            
            Query: {query}
            """
        ])
        
        return {
            "page_id": page["id"],
            "response": response.text
        }
    except Exception as e:
        print(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page["id"],
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
