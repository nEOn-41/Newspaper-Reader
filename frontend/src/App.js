import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';

function App() {
  const [file, setFile] = useState(null);
  const [publicationName, setPublicationName] = useState('');
  const [edition, setEdition] = useState('');
  const [date, setDate] = useState('');
  const [pdfId, setPdfId] = useState(null);
  const [responses, setResponses] = useState([]);
  const [pdfs, setPdfs] = useState([]);
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [newClientName, setNewClientName] = useState('');
  const [newClientKeywords, setNewClientKeywords] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);

  const [publications] = useState([
    { value: 'The Times of India', label: 'The Times of India' }
  ]);
  const [editions] = useState([
    'Hyderabad', 'Pune', 'Ahmedabad', 'Bengaluru', 'Mumbai',
    'Kochi', 'Lucknow', 'Delhi', 'Goa', 'Chandigarh',
    'Chennai', 'Jaipur', 'Kolkata', 'Bhopal'
  ].map(city => ({ value: city, label: city })));

  useEffect(() => {
    fetchPDFs();
    fetchClients();
  }, []);

  const fetchPDFs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/list-pdfs');
      setPdfs(response.data.pdfs);
    } catch (error) {
      console.error('Error fetching PDFs:', error);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await axios.get('http://localhost:8000/clients');
      setClients(response.data.clients);
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  };

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
      alert('PDF uploaded successfully and stored in the DATA folder!');
      fetchPDFs();  // Add this line to refresh the PDF list
      // Clear the form fields after successful upload
      setFile(null);
      setPublicationName('');
      setEdition('');
      setDate('');
    } catch (error) {
      console.error('Error uploading file:', error);
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
      }
      alert('Error uploading file. Please try again.');
    }
    fetchPDFs();  // Refresh the list of PDFs  
  };

  const handleAddClient = async () => {
    if (!newClientName || !newClientKeywords) {
      alert('Please enter a client name and keywords!');
      return;
    }
    try {
      await axios.post('http://localhost:8000/clients', {
        name: newClientName,
        keywords: newClientKeywords.split(',').map(k => k.trim())
      });
      setNewClientName('');
      setNewClientKeywords('');
      fetchClients();
    } catch (error) {
      console.error('Error adding client:', error);
      alert('Error adding client. Please try again.');
    }
  };

  const handleQueryClient = async () => {
    if (!selectedClient) {
      alert('Please select a client!');
      return;
    }

    setIsQuerying(true);
    try {
      const response = await axios.post('http://localhost:8000/query', {
        client: selectedClient.value
      });
      
      const validResponses = response.data.responses.map(item => {
        try {
          return {
            ...item,
            response: JSON.parse(item.response)
          };
        } catch (error) {
          console.error(`Error parsing JSON for page ${item.page_id}:`, error);
          return {
            ...item,
            response: { retrieval: false, error: "Invalid JSON response" }
          };
        }
      });

      setResponses(validResponses);
    } catch (error) {
      console.error('Error querying PDFs:', error);
      alert('Error querying PDFs. Please try again.');
    }
    setIsQuerying(false);
  };

  const handleDeleteClient = async (clientName) => {
    try {
      await axios.delete(`http://localhost:8000/clients/${clientName}`);
      fetchClients();
    } catch (error) {
      console.error('Error deleting client:', error);
      alert('Error deleting client. Please try again.');
    }
  };

  const handleDelete = async (pdfId) => {
    try {
      await axios.delete(`http://localhost:8000/delete-pdf/${pdfId}`);
      alert('PDF deleted successfully!');
      fetchPDFs();
    } catch (error) {
      console.error('Error deleting PDF:', error);
      alert('Error deleting PDF. Please try again.');
    }
  };

  const handlePublicationChange = (selectedOption) => {
    setPublicationName(selectedOption ? selectedOption.value : '');
  };

  const handleEditionChange = (selectedOption) => {
    setEdition(selectedOption ? selectedOption.value : '');
  };

  return (
    <div className="App">
      <h1>Newspaper Query System</h1>
      <div>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <Select
          value={publications.find(pub => pub.value === publicationName)}
          onChange={handlePublicationChange}
          options={publications}
          placeholder="Select Publication"
          isClearable
        />
        <Select
          value={editions.find(ed => ed.value === edition)}
          onChange={handleEditionChange}
          options={editions}
          placeholder="Select Edition"
          isClearable
        />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button onClick={handleUpload}>Upload PDF</button>
      </div>
      <h2>Client Management</h2>
      <div>
        <input
          type="text"
          value={newClientName}
          onChange={(e) => setNewClientName(e.target.value)}
          placeholder="Enter client name"
        />
        <input
          type="text"
          value={newClientKeywords}
          onChange={(e) => setNewClientKeywords(e.target.value)}
          placeholder="Enter keywords (comma-separated)"
        />
        <button onClick={handleAddClient}>Add Client</button>
      </div>
      <Select
        value={selectedClient}
        onChange={setSelectedClient}
        options={clients.map(client => ({ value: client.name, label: client.name }))}
        placeholder="Select Client"
      />
      {selectedClient && (
        <div>
          <h3>Keywords for {selectedClient.label}</h3>
          <ul>
            {clients.find(c => c.name === selectedClient.value).keywords.map((keyword, index) => (
              <li key={index}>{keyword}</li>
            ))}
          </ul>
          <button onClick={handleQueryClient} disabled={isQuerying}>
            {isQuerying ? 'Querying...' : 'Query Client'}
          </button>
          <button onClick={() => handleDeleteClient(selectedClient.value)}>Delete Client</button>
        </div>
      )}
      <h2>Uploaded PDFs</h2>
      <ul>
        {pdfs.map((pdf) => (
          <li key={pdf.pdf_id}>
            {pdf.publication_name} - {pdf.edition} ({pdf.date}) - {pdf.page_count} pages
            <button onClick={() => handleDelete(pdf.pdf_id)}>Delete</button>
          </li>
        ))}
      </ul>
      {responses.length > 0 && (
        <div>
          <h2>Responses:</h2>
          {responses.map((response, index) => (
            <div key={index}>
              <h3>Page ID: {response.page_id}</h3>
              {response.response.error ? (
                <p>Error: {response.response.error}</p>
              ) : (
                <div>
                  <p><strong>Reasoning:</strong> {response.response.reasoning}</p>
                  <p><strong>Retrieval:</strong> {response.response.retrieval ? 'Yes' : 'No'}</p>
                  {response.response.keywords && (
                    <div>
                      <h4>Keywords Found:</h4>
                      {response.response.keywords.map((keyword, kidx) => (
                        <div key={kidx}>
                          <h5>{keyword.keyword}</h5>
                          {keyword.articles.map((article, aidx) => (
                            <div key={aidx}>
                              <p><strong>Headline:</strong> {article.headline}</p>
                              <p><strong>Summary:</strong> {article.summary}</p>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
