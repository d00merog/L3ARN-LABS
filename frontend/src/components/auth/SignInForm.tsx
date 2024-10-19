import React, { useState } from 'react';
import { TextField, Button, Paper, Typography } from '@mui/material';

interface SignInFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
}

const SignInForm: React.FC<SignInFormProps> = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(email, password);
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, margin: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Sign In
      </Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Email"
          variant="outlined"
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <TextField
          fullWidth
          label="Password"
          type="password"
          variant="outlined"
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          size="large"
          sx={{ mt: 2 }}
        >
          Sign In
        </Button>
      </form>
    </Paper>
  );
};

export default SignInForm;
