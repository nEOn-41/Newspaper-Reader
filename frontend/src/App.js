import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';

function App() {
  const [file, setFile] = useState(null);
  const [publicationName, setPublicationName] = useState('');
  const [edition, setEdition] = useState('');
  const [date, setDate] = useState('');
  const [pdfId, setPdfId] = useState(null);
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState([]);
  const [pdfs, setPdfs] = useState([]);

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
  }, []);

  const fetchPDFs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/list-pdfs');
      setPdfs(response.data.pdfs);
    } catch (error) {
      console.error('Error fetching PDFs:', error);
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
      alert('PDF uploaded successfully!');
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
  };

  const handleQuery = async () => {
    if (!query) {
      alert('Please enter a query!');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/query', {
        query: query,
      });
      
      // Filter responses to only include those with retrieval: true
      const filteredResponses = response.data.responses.filter(resp => {
        try {
          const parsedResponse = JSON.parse(resp.response);
          return parsedResponse.retrieval === true;
        } catch (error) {
          console.error('Error parsing response:', error);
          return false;
        }
      });

      setResponses(filteredResponses);
    } catch (error) {
      console.error('Error querying PDF:', error);
      alert('Error querying PDF. Please try again.');
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
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query"
        />
        <button onClick={handleQuery}>Submit Query</button>
      </div>
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
          {responses.map((response, index) => {
            try {
              const parsedResponse = JSON.parse(response.response);
              return (
                <div key={index}>
                  <h3>Page ID: {response.page_id}</h3>
                  {parsedResponse.keywords.map((keyword, keywordIndex) => (
                    <div key={keywordIndex}>
                      <h4>Keyword: {keyword.keyword}</h4>
                      {keyword.articles.map((article, articleIndex) => (
                        <div key={articleIndex}>
                          <h5>{article.headline}</h5>
                          <p>{article.summary}</p>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              );
            } catch (error) {
              console.error('Error parsing response:', error);
              return null;
            }
          })}
        </div>
      )}
    </div>
  );
}

export default App;
