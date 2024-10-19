import React, { useState } from 'react';
import api from '../../utils/api';
import Button from '../common/button';

const LanguageInput: React.FC = () => {
  const [text, setText] = useState('');
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  const handleTextSubmit = async () => {
    try {
      await api.post('/language-preservation/text', { text });
      setText('');
      alert('Text submitted successfully!');
    } catch (error) {
      console.error('Error submitting text:', error);
      alert('Failed to submit text. Please try again.');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);

      const chunks: BlobPart[] = [];
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => setAudioBlob(new Blob(chunks, { type: 'audio/webm' }));

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const handleAudioSubmit = async () => {
    if (audioBlob) {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      try {
        await api.post('/language-preservation/audio', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setAudioBlob(null);
        alert('Audio submitted successfully!');
      } catch (error) {
        console.error('Error submitting audio:', error);
        alert('Failed to submit audio. Please try again.');
      }
    }
  };

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">Contribute to Language Preservation</h2>
      <div className="mb-4">
        <textarea
          className="w-full p-2 border rounded"
          rows={5}
          value={text}
          onChange={handleTextChange}
          placeholder="Enter text in the language you're preserving..."
        />
        <Button onClick={handleTextSubmit} className="mt-2">Submit Text</Button>
      </div>
      <div>
        <Button onClick={isRecording ? stopRecording : startRecording}>
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </Button>
        {audioBlob && (
          <Button onClick={handleAudioSubmit} className="ml-2">
            Submit Audio
          </Button>
        )}
      </div>
    </div>
  );
};

export default LanguageInput;
