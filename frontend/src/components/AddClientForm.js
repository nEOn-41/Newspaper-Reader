import React, { useState } from 'react';
import axios from 'axios';

const AddClientForm = ({ fetchClients }) => {
  const [newClientName, setNewClientName] = useState('');
  const [newClientKeywords, setNewClientKeywords] = useState('');
  const [newClientDetails, setNewClientDetails] = useState('');

  const handleAddClient = async () => {
    if (!newClientName || !newClientKeywords || !newClientDetails) {
      alert('Please enter a client name, keywords, and details!');
      return;
    }
    try {
      await axios.post('http://localhost:8000/clients', {
        name: newClientName,
        keywords: newClientKeywords.split(',').map(k => k.trim()),
        details: newClientDetails
      });
      setNewClientName('');
      setNewClientKeywords('');
      setNewClientDetails('');
      fetchClients();
    } catch (error) {
      console.error('Error adding client:', error);
      alert('Error adding client. Please try again.');
    }
  };

  return (
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
      <textarea
        value={newClientDetails}
        onChange={(e) => setNewClientDetails(e.target.value)}
        placeholder="Enter client details"
      />
      <button onClick={handleAddClient}>Add Client</button>
    </div>
  );
};

export default AddClientForm;
