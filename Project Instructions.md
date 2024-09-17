### **Objective**:
We are building an automated media monitoring tool designed to help clients track media coverage by analyzing newspaper pages for specific keywords. This tool will streamline the process by automating keyword matching using AI, reducing the need for manual checks. The system leverages the **Gemini 1.5 Flash model** to process e-newspapers (PDFs) and respond based on client-specific keywords.

### **Key Features**:

1. **PDF Upload with Metadata**:
   - Users upload PDFs of newspapers and provide additional metadata such as:
     - **Publication Name**: The name of the newspaper (e.g., Times of India).
     - **Edition**: The specific edition of the newspaper (e.g., Chandigarh, Ahmedabad, Pune).
     - **Date**: The date corresponding to the newspaper edition (provided by the user).

2. **PDF Page Extraction**:
   - Each PDF is split into individual pages, which are converted into **image** format.
   - A unique **ID** is generated for each page by concatenating the **Source** (PDF file name) and the **Page Number**.
   - Metadata is associated with each page:
     - **Source**: The PDF file name.
     - **Publication Name**: Provided by the user during upload.
     - **Edition**: Provided by the user during upload.
     - **Date**: Provided by the user during upload.
     - **Page Number**: The page number within the PDF.
     - **ID**: The concatenated string of Source and Page Number.

3. **Client and Keyword Management**:
   - Users can **add clients** through the interface.
   - Each client will have a set of **keywords** attached to them, which will be used to search through the uploaded newspaper pages.
   - Keywords for each client are saved in the database and can be updated or removed as necessary.

4. **Query Processing**:
   - Users submit a query based on the client, and the system automatically adds:
     - A **system prompt**, which is editable in the frontend.
     - An **additional query** before sending keywords to the Gemini API. For example: "Please provide the headlines with the page number if the article contains anything related to the following words."
     - A **set of keywords** specific to the client.
   - The system processes one page at a time, sending the **page image** and associated metadata to the Gemini 1.5 Flash model.
   - The **page ID** is used to associate each page's respective response.

5. **Validation Layer (Second LLM)**:
   - **(Yet to be implemented)**: A second LLM layer will validate the responses from the first LLM (Gemini) and assess whether the keywords are correctly matched to the articles.
   - This layer will verify whether the keywords are relevant to the article and return a validation response in JSON format, indicating whether the match is valid or not.

6. **Invalid JSON Handling**:
   - A mechanism has been introduced to handle situations where the Gemini API returns invalid JSON responses.
   - If an invalid JSON structure is detected, the system retries calling the Gemini API for only those responses that returned invalid JSON, ensuring valid results.

7. **Batching and Rate Limit Handling**:
   - A central **pipeline** processes all requests sent to the Gemini API, including queries and retries for invalid JSON. This pipeline ensures compliance with the free-tier rate limit of **15 requests per minute**.
   - The system uses a sliding window approach to track requests:
     - A buffer keeps track of the timestamps of requests sent in the last 60 seconds.
     - New requests are processed as soon as slots become available in the buffer.
     - The system can send up to 15 requests at once if the buffer allows.
   - Additional requests are added to a **queue** and processed as soon as slots become available in the sliding window.

8. **Multi-modal Processing**:
   - The system leverages the multi-modal capability of the **Gemini 1.5 Flash model** to process images of newspaper pages, enabling it to "see" and "read" the content (e.g., tables, images, text) on each page.

9. **Stage 1 Focus**:
   - In Stage 1, the system will query **multiple editions** of a single publication. For example, querying all relevant pages from the **Times of India** across different editions (e.g., Chandigarh, Ahmedabad, Pune) based on the client's keywords.
   - Each edition's pages will have their own response, identified by their **page ID**.

### **Development Components**:

1. **Backend**:
   - **PDF Upload API**: Create an endpoint that accepts PDF uploads along with user-provided metadata (Publication Name, Edition, Date).
   - **Client & Keyword Management**: Implement functionality to add and manage clients and the keywords associated with each client.
   - **Page Extraction & Metadata**: Implement logic to extract individual pages, convert them into images, and associate each page with its metadata and unique ID.
   - **Query API**: Develop an API that accepts user queries based on clients and their keywords, sends individual page images with their metadata to the Gemini API, and returns a relevant response.
   - **Invalid JSON Handling**: Implement retry mechanisms for invalid JSON responses from the Gemini API.
   - **Batching & Rate Limiting**: A centralized pipeline handles all requests sent to Gemini API, implementing a sliding window approach to enforce the 15 requests-per-minute limit. It queues additional requests and processes them as soon as slots become available.

2. **Frontend**:
   - A simple UI allowing users to:
     - Upload PDFs and provide metadata (Publication Name, Edition, Date).
     - Manage clients and assign keywords to them.
     - Input queries based on the selected client and their keywords.
     - View the results of the queries, with responses associated with the corresponding page IDs.
   - Allow users to edit the **system prompt** for the first LLM layer before submitting the query.

3. **Model Integration**:
   - **First LLM Layer (Gemini 1.5 Flash)**: Integrate the Gemini 1.5 Flash model to handle multi-modal document processing (images of newspaper pages). Use the editable system prompt and additional query before submitting the keywords.
   - **Second LLM Layer**: Integrate the second LLM layer to validate keyword-article matches based on the responses from the first LLM layer.

### **Initial Testing**:
For initial testing:
   - Process **one query at a time**, focusing on querying individual pages extracted from multiple newspaper editions.
   - Ensure that rate limits are respected and that responses are correctly associated with their respective page IDs.