
# Documentation

## Overview

This documentation provides a detailed guide to the **Media Monitoring Tool**, a system designed for clients to monitor sentiments, news, and policies related to them in the media. The tool uses **Gemini LLMs** for analyzing newspaper PDFs and extracting relevant information based on keywords provided by clients. The backend is built using FastAPI, the frontend with React, and the database is powered by PostgreSQL.

---

## System Features

1. **PDF Upload and Processing**:
   - Extract pages from PDFs and store metadata in a database.
   - Save extracted pages as images for further analysis.

2. **Client Management**:
   - Add, update, and delete client information.
   - Manage keywords for each client.

3. **Query Processing**:
   - Use client keywords to analyze PDFs with Gemini LLMs.
   - Validate results using two-layered LLM analysis.

4. **Frontend Interface**:
   - User-friendly React interface for managing PDFs, clients, and queries.
   - View query results with detailed keyword-article matches.

5. **Error Handling and Logging**:
   - Comprehensive error messages for invalid inputs or system failures.
   - Logging system for debugging and monitoring.

---

## Backend

### 1. Key Technologies
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **PDF Processing**: PyMuPDF and Pillow for page extraction
- **LLM Integration**: Google Gemini API

### 2. Workflow

#### PDF Upload
1. PDFs are uploaded through the frontend.
2. Backend processes the PDF using PyMuPDF to extract pages as PNG images.
3. Metadata such as publication name, edition, and date are saved in the database.

#### Query Processing
1. Keywords and additional queries are fetched for the client.
2. Pages are processed in two LLM layers:
   - **Layer One (Gemini Flash)**: Extracts information using keywords.
   - **Layer Two (Gemini Pro)**: Validates the extracted information.
3. Results are returned as JSON responses.

#### Client Management
- Manage client-specific keywords and details through dedicated API endpoints.
- Client data is stored in PostgreSQL for quick retrieval.

### 3. API Endpoints

| Endpoint                  | Method | Description                              |
|---------------------------|--------|------------------------------------------|
| `/upload-pdf`             | POST   | Upload and process PDFs.                 |
| `/clients`                | GET    | Retrieve all clients.                    |
| `/clients`                | POST   | Add a new client.                        |
| `/clients/{client_name}`  | PUT    | Update client details.                   |
| `/clients/{client_name}`  | DELETE | Delete a client.                         |
| `/query`                  | POST   | Query PDFs using client keywords.        |

### 4. Configuration

- **Environment Variables (`.env`)**:
  ```plaintext
  GEMINI_API_KEY=your-api-key
  DATABASE_URL=postgresql://user:password@localhost/newspaper_reader
  LOG_LEVEL=INFO
  ```

- **Logging**:
  - Logs are stored in `DATA/app.log`.
  - Use the `LOG_LEVEL` environment variable to control verbosity.

---

## Frontend

### 1. Key Components

#### PDF Upload
- Upload PDFs and provide metadata (publication, edition, date).
- Uses React-Select for dropdowns and Axios for API communication.

#### Client Management
- Add, view, update, and delete clients.
- Assign keywords to clients for targeted queries.

#### Query Results
- Display results from Gemini Flash and Gemini Pro in an easy-to-read format.
- Highlight keyword matches and provide detailed articles.

#### System Prompt Editor
- Allows admins to modify the system prompt and additional query.

### 2. Technologies
- **React**: Frontend framework.
- **Axios**: For HTTP requests.
- **React-Select**: For dropdown components.

### 3. Running the Frontend
- Install dependencies:
  ```bash
  npm install
  ```
- Start the development server:
  ```bash
  npm start
  ```
- Accessible at `http://localhost:3000`.

---

## Database

### 1. Schema

#### PDFs
- **Table**: `pdfs`
- **Fields**:
  - `id`: Unique identifier.
  - `publication_name`, `edition`, `date`, `total_pages`, `upload_date`.

#### Pages
- **Table**: `pages`
- **Fields**:
  - `id`: Unique identifier.
  - `pdf_id`: Foreign key linking to `pdfs`.
  - `page_number`, `image_path`.

#### Clients
- **Table**: `clients`
- **Fields**:
  - `id`: Unique identifier.
  - `name`, `keywords`, `details`.

#### System Prompts
- **Table**: `system_prompts`
- **Fields**:
  - `id`: Unique identifier.
  - `prompt`, `additional_query`.

### 2. Database Setup
- Initialize the database using Alembic migrations:
  ```bash
  alembic upgrade head
  ```

---

## Deployment

### 1. Local Deployment
1. Clone the repository:
   ```bash
   git clone https://github.com/nEOn-41/Newspaper-Reader.git
   ```
2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   alembic upgrade head
   ```
3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

### 2. Future Cloud Deployment
- Use Docker containers for backend and frontend.
- Configure environment variables securely in cloud platforms.

---

## Troubleshooting

| Issue                         | Solution                                      |
|-------------------------------|-----------------------------------------------|
| API key errors                | Verify `GEMINI_API_KEY` in `.env`.            |
| Database connection failures  | Ensure PostgreSQL is running and accessible. |
| PDF upload errors             | Check file format and PyMuPDF installation.  |
| LLM rate-limit errors         | Adjust batch size in `config.py`.            |

---

## Future Enhancements

1. **Authentication and Authorization**:
   - Role-based access control for multiple users.

2. **Scalability**:
   - Optimize for larger PDFs and high concurrency.

3. **Additional Integrations**:
   - Incorporate more LLMs or media sources.

4. **Advanced Analytics**:
   - Sentiment analysis and trend tracking.

---

## Conclusion

This media monitoring tool combines LLM capabilities with robust backend and frontend systems to provide an efficient solution for extracting and analyzing media content. For additional details, refer to the README or contact the project maintainer.
