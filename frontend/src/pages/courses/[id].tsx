import React from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/layout';
import CourseDetails from '../../components/course/course-details';

const CoursePage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;

  return (
    <Layout title="Course Details | Education Platform">
      <h1>Course Details</h1>
      {id && <CourseDetails courseId={Number(id)} />}
    </Layout>
  );
};

export default CoursePage;