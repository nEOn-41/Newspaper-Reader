import React, { useState } from 'react';
import Select from 'react-select';
import axios from 'axios';
import { publications, editions } from '../constants';

const PDFUpload = ({ fetchPDFs }) => {
  const [file, setFile] = useState(null);
  const [publicationName, setPublicationName] = useState('');
  const [edition, setEdition] = useState('');
  const [date, setDate] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handlePublicationChange = (selectedOption) => {
    setPublicationName(selectedOption ? selectedOption.value : '');
  };

  const handleEditionChange = (selectedOption) => {
    setEdition(selectedOption ? selectedOption.value : '');
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
      await axios.post('http://localhost:8000/upload-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      alert('PDF uploaded successfully and stored in the DATA folder!');
      fetchPDFs();
      setFile(null);
      setPublicationName('');
      setEdition('');
      setDate('');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
    }
  };

  return (
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
  );
};

export default PDFUpload;
