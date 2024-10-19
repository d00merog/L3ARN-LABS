import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import LessonViewer from '@/components/lessons/LessonViewer';
import CourseProgress from '@/components/courses/CourseProgress';
import CourseReviews from '@/components/courses/CourseReviews';
import { useSession } from 'next-auth/react';

interface Lesson {
  id: number;
  title: string;
  content: string;
  // Add other relevant fields
}

const CoursePage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const { data: session } = useSession();
  const [lesson, setLesson] = useState<Lesson | null>(null);

  useEffect(() => {
    const fetchLesson = async () => {
      if (id) {
        // Replace this with your actual API call to fetch the lesson
        const response = await fetch(`/api/lessons/${id}`);
        const data = await response.json();
        setLesson(data);
      }
    };

    fetchLesson();
  }, [id]);

  return (
    <Layout title="Course Details | Education Platform">
      <h1 className="text-3xl font-bold mb-6">Course Details</h1>
      {id && session?.user && session.user.id && (
        <CourseProgress courseId={Number(id)} userId={session.user.id} />
      )}
      {lesson && <LessonViewer lesson={lesson} />}
      {id && <CourseReviews courseId={Number(id)} />}
    </Layout>
  );
};

export default CoursePage;
