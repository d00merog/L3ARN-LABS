import React, { useState } from 'react';
import api from '../../utils/api';

const LanguageInput: React.FC = () => {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  const handleSubmit = async () => {
    try {
      await api.post('/language-preservation/submit', { text });
      setText('');
      alert('Language sample submitted successfully!');
    } catch (error) {
      console.error('Error submitting language sample:', error);
      alert('Failed to submit language sample. Please try again.');
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Here you would typically start/stop actual audio recording
    // and handle the recorded audio data
  };

  return (
    <div>
      <h2>Contribute to Language Preservation</h2>
      <textarea
        value={text}
        onChange={handleTextChange}
        placeholder="Enter text in the language you're preserving..."
        rows={5}
        cols={50}
      />
      <button onClick={handleSubmit}>Submit Text</button>
      <button onClick={toggleRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
    </div>
  );
};

export default LanguageInput;