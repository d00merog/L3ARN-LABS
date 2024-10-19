import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import CourseList from '@/components/courses/CourseList';
import CourseSearch from '@/components/courses/CourseSearch';
import { getAllCourses } from '@/api/courses';
import { useSession } from 'next-auth/react';
import { Course } from '@/types/course';

const CoursesPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const fetchedCourses = await getAllCourses();
        setCourses(fetchedCourses);
      } catch (error) {
        console.error('Error fetching courses:', error);
        setError('Failed to load courses. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (status !== 'loading') {
      fetchCourses();
    }
  }, [status]);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    }
  }, [status, router]);

  if (status === 'loading' || isLoading) {
    return <Layout title="Courses | Education Platform">Loading...</Layout>;
  }

  return (
    <Layout title="Courses | Education Platform">
      <h1 className="text-3xl font-bold mb-6">Courses</h1>
      <CourseSearch />
      {error ? (
        <p className="text-red-500">{error}</p>
      ) : (
        <CourseList courses={courses} />
      )}
    </Layout>
  );
};

export default CoursesPage;
