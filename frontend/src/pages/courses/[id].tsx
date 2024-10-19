import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import { Box, CircularProgress } from '@mui/material';
import { getCourse, enrollInCourse } from '@/api/courses';
import { Course } from '@/types/course';
import CourseDetails from '@/components/courses/CourseDetails';

const CoursePage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourse = async () => {
      if (typeof id === 'string') {
        try {
          const fetchedCourse = await getCourse(id);
          setCourse(fetchedCourse);
        } catch (error) {
          console.error('Error fetching course:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchCourse();
  }, [id]);

  const handleEnroll = async () => {
    if (course) {
      try {
        await enrollInCourse(course.id.toString());
        router.push('/dashboard');
      } catch (error) {
        console.error('Error enrolling in course:', error);
      }
    }
  };

  if (loading) {
    return (
      <Layout title="Loading... | AI-Powered Learning Platform">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  if (!course) {
    return <Layout title="Course Not Found | AI-Powered Learning Platform">Course not found</Layout>;
  }

  return (
    <Layout title={`${course.title} | AI-Powered Learning Platform`}>
      <CourseDetails course={course} onEnroll={handleEnroll} />
    </Layout>
  );
};

export default CoursePage;
