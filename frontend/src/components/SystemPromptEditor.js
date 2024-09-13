import React from 'react';
import axios from 'axios';

const SystemPromptEditor = ({ systemPrompt, setSystemPrompt, additionalQuery, setAdditionalQuery }) => {

  const handleUpdateSystemPrompt = async () => {
    try {
      await axios.post('http://localhost:8000/system-prompt', {
        system_prompt: systemPrompt,
        additional_query: additionalQuery
      });
      alert('System prompt and additional query updated successfully!');
    } catch (error) {
      console.error('Error updating system prompt:', error);
      alert('Error updating system prompt and additional query. Please try again.');
    }
  };

  return (
    <div>
      <h2>System Prompt and Additional Query</h2>
      <textarea
        value={systemPrompt}
        onChange={(e) => setSystemPrompt(e.target.value)}
        placeholder="Enter system prompt"
        rows={5}
        cols={50}
      />
      <textarea
        value={additionalQuery}
        onChange={(e) => setAdditionalQuery(e.target.value)}
        placeholder="Enter additional query"
        rows={2}
        cols={50}
      />
      <button onClick={handleUpdateSystemPrompt}>Update System Prompt and Additional Query</button>
    </div>
  );
};

export default SystemPromptEditor;
