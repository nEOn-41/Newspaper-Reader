import React from 'react';
import Select from 'react-select';

const ClientSelector = ({ clients, selectedClient, setSelectedClient }) => {
  return (
    <Select
      value={selectedClient}
      onChange={setSelectedClient}
      options={clients.map(client => ({ value: client.name, label: client.name }))}
      placeholder="Select Client"
    />
  );
};

export default ClientSelector;
