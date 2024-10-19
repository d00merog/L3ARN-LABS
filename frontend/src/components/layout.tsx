import React from 'react';
import Head from 'next/head';
import { Box, Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import dynamic from 'next/dynamic';

const Navbar = dynamic(() => import('./Navbar'), { ssr: false });
const Footer = dynamic(() => import('./Footer'), { ssr: false });

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const Layout: React.FC<LayoutProps> = ({ children, title = 'AI-Powered Learning Platform' }) => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box display="flex" flexDirection="column" minHeight="100vh">
        <Head>
          <title>{title}</title>
          <meta charSet="utf-8" />
          <meta name="viewport" content="initial-scale=1.0, width=device-width" />
          <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
        </Head>
        <Navbar />
        <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
          {children}
        </Container>
        <Footer />
      </Box>
    </ThemeProvider>
  );
};

export default Layout;
