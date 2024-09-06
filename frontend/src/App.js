import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [cacheId, setCacheId] = useState(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setCacheId(response.data.cache_id);
      alert('PDF uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
    }
  };

  const handleQuery = async () => {
    if (!cacheId) {
      alert('Please upload a PDF first!');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/query', {
        cache_id: cacheId,
        query: query,
      });
      setResponse(response.data.response);
    } catch (error) {
      console.error('Error querying PDF:', error);
      alert('Error querying PDF. Please try again.');
    }
  };

  return (
    <div className="App">
      <h1>PDF Query System</h1>
      <div>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
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
      {response && (
        <div>
          <h2>Response:</h2>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}

export default App;
