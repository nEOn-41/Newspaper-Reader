import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [publicationName, setPublicationName] = useState('');
  const [edition, setEdition] = useState('');
  const [date, setDate] = useState('');
  const [pdfId, setPdfId] = useState(null);
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState([]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file || !publicationName || !edition || !date) {
      alert('Please fill in all fields and select a file!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('publication_name', publicationName);
    formData.append('edition', edition);
    formData.append('date', date);

    try {
      const response = await axios.post('http://localhost:8000/upload-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setPdfId(response.data.pdf_id);
      alert('PDF uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error);
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
      }
      alert('Error uploading file. Please try again.');
    }
  };

  const handleQuery = async () => {
    if (!pdfId) {
      alert('Please upload a PDF first!');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/query', {
        pdf_id: pdfId,
        query: query,
      });
      setResponses(response.data.responses);
    } catch (error) {
      console.error('Error querying PDF:', error);
      alert('Error querying PDF. Please try again.');
    }
  };

  return (
    <div className="App">
      <h1>Newspaper Query System</h1>
      <div>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <input
          type="text"
          value={publicationName}
          onChange={(e) => setPublicationName(e.target.value)}
          placeholder="Publication Name"
        />
        <input
          type="text"
          value={edition}
          onChange={(e) => setEdition(e.target.value)}
          placeholder="Edition"
        />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button onClick={handleUpload}>Upload PDF</button>
      </div>
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query"
        />
        <button onClick={handleQuery}>Submit Query</button>
      </div>
      {responses.length > 0 && (
        <div>
          <h2>Responses:</h2>
          {responses.map((response, index) => (
            <div key={index}>
              <h3>Page ID: {response.page_id}</h3>
              <p>{response.response || response.error}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
