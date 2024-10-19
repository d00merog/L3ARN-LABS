import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/layout';
import { Typography, Button, Grid, Card, CardContent, CardActions, Box, Container, Paper, Snackbar } from '@mui/material';
import { useSession, signIn } from "next-auth/react";
import Image from 'next/image';
import SignInForm from '../components/auth/SignInForm';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import Web3SignIn from '../components/auth/Web3SignIn';

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref,
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const Home: React.FC = () => {
  const { data: session } = useSession();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const features = [
    { title: 'Personalized Learning', description: 'AI-powered courses tailored to your needs', icon: '/icons/personalized.svg' },
    { title: 'Interactive Lessons', description: 'Engage with dynamic content and real-time feedback', icon: '/icons/interactive.svg' },
    { title: 'Language Preservation', description: 'Contribute to preserving endangered languages', icon: '/icons/language.svg' },
    { title: 'Expert Instructors', description: 'Learn from AI agents specialized in various fields', icon: '/icons/expert.svg' },
  ];

  const handleSignIn = async (email: string, password: string) => {
    const result = await signIn('credentials', {
      redirect: false,
      email,
      password,
    });

    if (result?.error) {
      setError(result.error);
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <Layout title="Welcome | AI-Powered Learning Platform">
      <Box
        sx={{
          bgcolor: 'background.paper',
          pt: 8,
          pb: 6,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                component="h1"
                variant="h2"
                color="text.primary"
                gutterBottom
              >
                Welcome to the Future of Learning
              </Typography>
              <Typography variant="h5" color="text.secondary" paragraph>
                Empower your education with AI-driven personalized courses
              </Typography>
              <Box sx={{ mt: 4 }}>
                {!session ? (
                  <Button variant="contained" color="primary" size="large" onClick={() => router.push('/signup')} sx={{ mr: 2 }}>
                    Get Started
                  </Button>
                ) : (
                  <Button variant="contained" color="primary" size="large" onClick={() => router.push('/dashboard')} sx={{ mr: 2 }}>
                    Go to Dashboard
                  </Button>
                )}
                <Button variant="outlined" color="primary" size="large" onClick={() => router.push('/courses')}>
                  Explore Courses
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              {!session && (
                <Paper elevation={3} sx={{ p: 4, maxWidth: 400, margin: 'auto' }}>
                  <Typography variant="h5" component="h2" gutterBottom>
                    Sign In
                  </Typography>
                  <SignInForm onSubmit={handleSignIn} />
                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Typography variant="body2" sx={{ mb: 1 }}>Or</Typography>
                    <Web3SignIn />
                  </Box>
                </Paper>
              )}
            </Grid>
          </Grid>
        </Container>
      </Box>
      <Container sx={{ py: 8 }} maxWidth="md">
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item key={index} xs={12} sm={6} md={3}>
              <Card
                sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              >
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                  <Image src={feature.icon} alt={feature.title} width={64} height={64} />
                </Box>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2" align="center">
                    {feature.title}
                  </Typography>
                  <Typography align="center">
                    {feature.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" fullWidth>Learn More</Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
      <Box sx={{ bgcolor: 'background.paper', p: 6 }} component="footer">
        <Typography variant="h6" align="center" gutterBottom>
          Join Our Community
        </Typography>
        <Typography
          variant="subtitle1"
          align="center"
          color="text.secondary"
          component="p"
        >
          Connect with learners and educators from around the world
        </Typography>
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
          <Button variant="outlined" color="primary" sx={{ mx: 1 }}>
            Forum
          </Button>
          <Button variant="outlined" color="primary" sx={{ mx: 1 }}>
            Blog
          </Button>
        </Box>
      </Box>
      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Layout>
  );
};

export default Home;
