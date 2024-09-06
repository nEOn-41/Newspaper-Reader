import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai import caching
import datetime
import asyncio
from dotenv import load_dotenv
import tempfile

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Read the uploaded file and write it to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Upload the PDF using the Files API
        pdf_file = genai.upload_file(temp_file_path, mime_type="application/pdf")
        print(f"Uploaded file '{pdf_file.display_name}' as: {pdf_file.uri}")
        
        # Wait for the file to finish processing
        while pdf_file.state.name == 'PROCESSING':
            print("Waiting for file to be processed...")
            await asyncio.sleep(2)
            pdf_file = genai.get_file(pdf_file.name)
        
        if pdf_file.state.name != 'ACTIVE':
            raise Exception(f"File {pdf_file.name} failed to process")
        
        print(f"File processing complete: {pdf_file.uri}")
        
        # Create a cache with a 15 minute TTL
        cache = caching.CachedContent.create(
            model='models/gemini-1.5-flash-001',
            display_name=f'PDF-{file.filename}',
            system_instruction=(
                'You are an expert PDF file analyzer. Your job is to answer '
                'the user\'s query based on the PDF file you have access to.'
            ),
            contents=[pdf_file],
            ttl=datetime.timedelta(minutes=15),
        )
        
        print(f"Cache created with ID: {cache.name}")
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return {"message": "PDF uploaded and cached successfully", "cache_id": cache.name}
    except Exception as e:
        print(f"Error in upload_pdf: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e.args}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

@app.post("/query")
async def query_pdf(cache_id: str, query: str):
    try:
        # Retrieve the cached content
        cache = caching.CachedContent.get(cache_id)
        
        # Construct a GenerativeModel which uses the created cache
        model = genai.GenerativeModel.from_cached_content(cached_content=cache)
        
        # Query the model
        response = model.generate_content(query)
        
        return {"response": response.text, "usage": response.usage_metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
