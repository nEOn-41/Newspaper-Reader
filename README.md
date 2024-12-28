
# README

## Introduction
This project processes newspaper PDFs, extracts their pages, and applies two layers of LLM-based analysis (Gemini models from Google Generative AI). The application is a **media monitoring tool** used by clients to track sentiments, news, and policies related to them in the media. It allows you to:

- **Upload** newspaper PDFs.
- **Extract** each PDF’s pages into images.
- **Manage** client information with specific keywords.
- **Query** PDFs using the client’s keywords.
- **Validate** extracted content with a second LLM layer.
- **Display** query results in a React-based UI.

## Features
- **Two-layer LLM pipeline:** First for extraction, second for validation.
- **PDF upload and metadata storage:** Automatic extraction of pages.
- **Client management:** Add, update, and delete client details.
- **Responsive frontend:** User-friendly interface for managing and querying data.
- **Database integration:** Uses PostgreSQL for storage and retrieval.

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/nEOn-41/Newspaper-Reader.git
   cd Newspaper-Reader
   ```

2. **Set up the Backend**
   - Navigate to the `backend/` directory:
     ```bash
     cd backend
     ```
   - Create and activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux/macOS
     .\venv\Scripts\activate  # Windows
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Add a `.env` file in the `backend/` folder with the following content:
     ```plaintext
     GEMINI_API_KEY=your-api-key
     DATABASE_URL=postgresql://user:password@localhost/newspaper_reader
     LOG_LEVEL=INFO
     ```
   - Initialize the database:
     ```bash
     alembic upgrade head
     ```

3. **Set up the Frontend**
   - Navigate to the `frontend/` directory:
     ```bash
     cd ../frontend
     ```
   - Install dependencies:
     ```bash
     npm install
     ```

## Running the Application

1. **Start the Backend**
   From the `backend` directory:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the Frontend**
   From the `frontend` directory:
   ```bash
   npm start
   ```

The application will now be accessible at:
- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend:** [http://localhost:8000](http://localhost:8000)

## Usage

### 1. Upload a PDF
- Use the **Upload PDF** section in the frontend to upload PDFs with metadata such as publication name, edition, and date.
- The backend will process the PDF, extract pages, and save metadata.

### 2. Manage Clients
- Add client information, including keywords for querying PDFs.
- View, update, or delete client details as needed.

### 3. Query PDFs
- Select a client and query the PDFs using their keywords.
- The results will show articles and keywords extracted by the Gemini models.

### 4. View Results
- Responses from both LLM layers will be displayed, including validation results.

## Troubleshooting

- **Invalid API Key:** Ensure the `GEMINI_API_KEY` in `.env` is correct.
- **Database Issues:** Confirm that PostgreSQL is running and `DATABASE_URL` is correctly set.
- **PDF Errors:** Ensure that valid PDF files are uploaded and dependencies like PyMuPDF are installed.
- **LLM Rate-Limits:** Adjust `BATCH_SIZE` and `RATE_LIMIT_INTERVAL` in `config.py` if rate-limit errors occur.
- **CORS Issues:** Ensure the frontend and backend are configured to work on different ports.

## Future Enhancements

- **Authentication:** Add support for multiple user roles.
- **Scaling:** Optimize PDF processing for larger files and higher concurrency.
- **Advanced LLM Integration:** Experiment with additional models beyond Gemini.

## Conclusion
This system is designed for efficient media monitoring by analyzing PDFs and keywords. For more detailed instructions, refer to the full documentation file.
