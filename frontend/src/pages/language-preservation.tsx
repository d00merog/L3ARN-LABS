import React from 'react';
import Head from 'next/head';
import Layout from '../components/layout';
import LanguageInput from '../components/language-preservation/LanguageInput';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import { Typography, Box, Paper } from '@mui/material';

const LanguagePreservationPage: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();

  React.useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  return (
    <Layout>
      <Head>
        <title>Language Preservation | AI-Powered Learning Platform</title>
        <meta name="description" content="Contribute to preserving endangered languages through text and audio samples" />
      </Head>
      <Box maxWidth={800} margin="auto">
        <Typography variant="h3" component="h1" gutterBottom>
          Language Preservation
        </Typography>
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="body1" paragraph>
            Help preserve endangered languages by contributing text and audio samples. Your contributions are valuable in our efforts to document and revitalize these languages.
          </Typography>
          <Typography variant="body1" paragraph>
            You can submit written text in the language you're helping to preserve, or record audio samples of spoken language. Every contribution, no matter how small, helps in our mission to protect linguistic diversity.
          </Typography>
        </Paper>
        <LanguageInput />
      </Box>
    </Layout>
  );
};

export default LanguagePreservationPage;
