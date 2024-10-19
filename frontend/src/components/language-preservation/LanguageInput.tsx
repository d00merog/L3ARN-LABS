import React, { useState } from 'react';
import api from '../../utils/api';
import { TextField, Button, Box, Typography, CircularProgress, Snackbar } from '@mui/material';
import { Alert } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';

const LanguageInput: React.FC = () => {
  const [text, setText] = useState('');
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  const handleTextSubmit = async () => {
    setIsLoading(true);
    try {
      await api.post('/language-preservation/text', { text });
      setText('');
      setSnackbar({ open: true, message: 'Text submitted successfully!', severity: 'success' });
    } catch (error) {
      console.error('Error submitting text:', error);
      setSnackbar({ open: true, message: 'Failed to submit text. Please try again.', severity: 'error' });
    } finally {
      setIsLoading(false);
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
      setSnackbar({ open: true, message: 'Failed to start recording. Please try again.', severity: 'error' });
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
      setIsLoading(true);
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      try {
        await api.post('/language-preservation/audio', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setAudioBlob(null);
        setSnackbar({ open: true, message: 'Audio submitted successfully!', severity: 'success' });
      } catch (error) {
        console.error('Error submitting audio:', error);
        setSnackbar({ open: true, message: 'Failed to submit audio. Please try again.', severity: 'error' });
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <Box sx={{ maxWidth: 600, margin: 'auto' }}>
      <Typography variant="h4" component="h2" gutterBottom>
        Contribute to Language Preservation
      </Typography>
      <TextField
        fullWidth
        multiline
        rows={4}
        variant="outlined"
        value={text}
        onChange={handleTextChange}
        placeholder="Enter text in the language you're preserving..."
        sx={{ mb: 2 }}
      />
      <Button
        variant="contained"
        color="primary"
        onClick={handleTextSubmit}
        disabled={isLoading || !text}
        sx={{ mb: 4 }}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Submit Text'}
      </Button>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Button
          variant="contained"
          color={isRecording ? 'secondary' : 'primary'}
          startIcon={isRecording ? <StopIcon /> : <MicIcon />}
          onClick={isRecording ? stopRecording : startRecording}
          sx={{ mr: 2 }}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </Button>
        {audioBlob && (
          <Button
            variant="contained"
            color="primary"
            onClick={handleAudioSubmit}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Submit Audio'}
          </Button>
        )}
      </Box>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LanguageInput;
