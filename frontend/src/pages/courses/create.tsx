import React from 'react';
import Layout from '@/components/layout';
import CourseCreationForm from '@/components/courses/CourseCreationForm';
import { Typography, Box } from '@mui/material';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

const CreateCoursePage: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();

  if (status === 'loading') {
    return <Layout title="Create Course | AI-Powered Learning Platform">Loading...</Layout>;
  }

  if (!session) {
    router.push('/login');
    return null;
  }

  return (
    <Layout title="Create Course | AI-Powered Learning Platform">
      <Box maxWidth={600} margin="auto">
        <Typography variant="h3" component="h1" gutterBottom>
          Create a New Course
        </Typography>
        <CourseCreationForm />
      </Box>
    </Layout>
  );
};

export default CreateCoursePage;
