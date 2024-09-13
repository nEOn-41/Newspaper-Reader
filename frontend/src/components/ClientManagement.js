import React, { useState } from 'react';
import AddClientForm from './AddClientForm';
import ClientSelector from './ClientSelector';
import ClientDetails from './ClientDetails';
import axios from 'axios';

const ClientManagement = ({ clients, fetchClients, setResponses, setIsQuerying, isQuerying, additionalQuery }) => {
  const [selectedClient, setSelectedClient] = useState(null);

  const handleQueryClient = async () => {
    if (!selectedClient) {
      alert('Please select a client!');
      return;
    }

    setIsQuerying(true);
    try {
      const clientData = clients.find(c => c.name === selectedClient.value);
      const response = await axios.post('http://localhost:8000/query', {
        client: selectedClient.value,
        keywords: clientData.keywords,
        additional_query: additionalQuery
      });
      setResponses(response.data.responses);
    } catch (error) {
      console.error('Error querying PDFs:', error);
      alert('Error querying PDFs. Please try again.');
    }
    setIsQuerying(false);
  };

  return (
    <div>
      <AddClientForm fetchClients={fetchClients} />
      <ClientSelector
        clients={clients}
        selectedClient={selectedClient}
        setSelectedClient={setSelectedClient}
      />
      {selectedClient && (
        <ClientDetails
          clients={clients}
          selectedClient={selectedClient}
          handleQueryClient={handleQueryClient}
          isQuerying={isQuerying}
          fetchClients={fetchClients}
        />
      )}
    </div>
  );
};

export default ClientManagement;
