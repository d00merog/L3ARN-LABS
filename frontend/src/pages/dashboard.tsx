import React, { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import CourseList from '@/components/courses/CourseList';
import api from '@/utils/api';

interface EnrolledCourse {
  id: number;
  title: string;
  progress: number;
}

const Dashboard: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [enrolledCourses, setEnrolledCourses] = useState<EnrolledCourse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    } else if (status === 'authenticated' && session?.user?.id) {
      fetchEnrolledCourses(session.user.id);
    }
  }, [status, session, router]);

  const fetchEnrolledCourses = async (userId: string) => {
    try {
      const response = await api.get(`/users/${userId}/enrolled-courses`);
      setEnrolledCourses(response.data);
    } catch (error) {
      console.error('Error fetching enrolled courses:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <Layout title="Dashboard | Education Platform">Loading...</Layout>;
  }

  return (
    <Layout title="Dashboard | Education Platform">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Your Enrolled Courses</h2>
        {enrolledCourses.length > 0 ? (
          <ul className="space-y-4">
            {enrolledCourses.map((course) => (
              <li key={course.id} className="border p-4 rounded-lg">
                <h3 className="text-xl font-semibold">{course.title}</h3>
                <div className="mt-2 bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{ width: `${course.progress}%` }}
                  ></div>
                </div>
                <p className="mt-1">Progress: {course.progress}%</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>You are not enrolled in any courses yet.</p>
        )}
      </section>
      <section>
        <h2 className="text-2xl font-semibold mb-4">Recommended Courses</h2>
        <CourseList featured={true} />
      </section>
    </Layout>
  );
};

export default Dashboard;
