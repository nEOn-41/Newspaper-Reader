import React from 'react';

const ResponsesDisplay = ({ responses }) => {
  return (
    <div>
      {responses.length > 0 && (
        <div>
          <h2>Responses:</h2>
          {responses.map((response, index) => (
            <div key={index}>
              <h3>Page ID: {response.page_id}</h3>
              <pre>{JSON.stringify(JSON.parse(response.response), null, 2)}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResponsesDisplay;
