import React from 'react';
import axios from 'axios';

const ClientDetails = ({ clients, selectedClient, handleQueryClient, isQuerying, fetchClients }) => {

  const clientData = clients.find(c => c.name === selectedClient.value);

  const handleDeleteClient = async () => {
    try {
      await axios.delete(`http://localhost:8000/clients/${selectedClient.value}`);
      fetchClients();
    } catch (error) {
      console.error('Error deleting client:', error);
      alert('Error deleting client. Please try again.');
    }
  };

  return (
    <div>
      <h3>Details for {selectedClient.label}</h3>
      <p>{clientData?.details}</p>
      <h3>Keywords for {selectedClient.label}</h3>
      <ul>
        {clientData?.keywords ? (
          clientData.keywords.map((keyword, index) => (
            <li key={index}>{keyword}</li>
          ))
        ) : (
          <li>No keywords found for this client</li>
        )}
      </ul>
      <button onClick={handleQueryClient} disabled={isQuerying}>
        {isQuerying ? 'Querying...' : 'Query Client'}
      </button>
      <button onClick={handleDeleteClient}>Delete Client</button>
    </div>
  );
};

export default ClientDetails;
