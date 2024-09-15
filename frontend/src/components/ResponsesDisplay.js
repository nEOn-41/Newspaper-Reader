import React from 'react';

const ResponsesDisplay = ({ responses }) => {
  const parseResponse = (response) => {
    if (typeof response === 'string') {
      try {
        return JSON.parse(response);
      } catch (error) {
        console.error('Error parsing response:', error);
        return response;
      }
    }
    return response;
  };

  return (
    <div>
      {responses.length > 0 && (
        <div>
          <h2>Responses:</h2>
          {responses.map((response, index) => (
            <div key={index}>
              <h3>Page ID: {response.page_id}</h3>
              <h4>First LLM Response:</h4>
              <pre>{JSON.stringify(parseResponse(response.first_response), null, 2)}</pre>
              {response.second_response && (
                <>
                  <h4>Second LLM Response:</h4>
                  <pre>{JSON.stringify(parseResponse(response.second_response), null, 2)}</pre>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResponsesDisplay;