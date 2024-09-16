import React from 'react';

const GlobalErrorHandler = ({ error, onClear }) => {
  if (!error) return null;

  return (
    <div className="global-error">
      <p>Error: {error}</p>
      <button onClick={onClear}>Dismiss</button>
    </div>
  );
};

export default GlobalErrorHandler;