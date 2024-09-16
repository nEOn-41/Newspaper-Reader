import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PDFUpload from './components/PDFUpload';
import ClientManagement from './components/ClientManagement';
import SystemPromptEditor from './components/SystemPromptEditor';
import UploadedPDFs from './components/UploadedPDFs';
import ResponsesDisplay from './components/ResponsesDisplay';
import ErrorBoundary from './components/ErrorBoundary';
import GlobalErrorHandler from './components/GlobalErrorHandler';

function App() {
  const [pdfs, setPdfs] = useState([]);
  const [clients, setClients] = useState([]);
  const [responses, setResponses] = useState([]);
  const [isQuerying, setIsQuerying] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [additionalQuery, setAdditionalQuery] = useState('');
  const [globalError, setGlobalError] = useState(null);

  useEffect(() => {
    fetchPDFs();
    fetchClients();
    fetchSystemPrompt();
  }, []);

  const fetchPDFs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/list-pdfs');
      setPdfs(response.data.pdfs);
    } catch (error) {
      handleError('Error fetching PDFs', error);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await axios.get('http://localhost:8000/clients');
      setClients(response.data.clients);
    } catch (error) {
      handleError('Error fetching clients', error);
    }
  };

  const fetchSystemPrompt = async () => {
    try {
      const response = await axios.get('http://localhost:8000/system-prompt');
      setSystemPrompt(response.data.system_prompt);
      setAdditionalQuery(response.data.additional_query);
    } catch (error) {
      handleError('Error fetching system prompt', error);
    }
  };

  const handleError = (message, error) => {
    console.error(message, error);
    setGlobalError(error.response?.data?.error || error.message || 'An unexpected error occurred');
  };

  return (
    <ErrorBoundary>
      <div className="App">
        <h1>Newspaper Query System</h1>
        <GlobalErrorHandler error={globalError} onClear={() => setGlobalError(null)} />
        <PDFUpload fetchPDFs={fetchPDFs} handleError={handleError} />
        <h2>Client Management</h2>
        <ClientManagement
          clients={clients}
          fetchClients={fetchClients}
          setResponses={setResponses}
          setIsQuerying={setIsQuerying}
          isQuerying={isQuerying}
          additionalQuery={additionalQuery}
          handleError={handleError}
        />
        <UploadedPDFs pdfs={pdfs} fetchPDFs={fetchPDFs} handleError={handleError} />
        <ResponsesDisplay responses={responses} />
        <SystemPromptEditor
          systemPrompt={systemPrompt}
          setSystemPrompt={setSystemPrompt}
          additionalQuery={additionalQuery}
          setAdditionalQuery={setAdditionalQuery}
          handleError={handleError}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;