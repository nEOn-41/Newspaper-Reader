import React from 'react';
import axios from 'axios';

const UploadedPDFs = ({ pdfs, fetchPDFs }) => {

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

  return (
    <div>
      <h2>Uploaded PDFs</h2>
      <ul>
        {pdfs.map((pdf) => (
          <li key={pdf.pdf_id}>
            {pdf.publication_name} - {pdf.edition} ({pdf.date}) - {pdf.page_count} pages
            <button onClick={() => handleDelete(pdf.pdf_id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UploadedPDFs;
