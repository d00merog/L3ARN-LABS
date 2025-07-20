import React from 'react';
import Layout from '@/components/layout';
import Quiz from '@/components/quiz/Quiz';

const QuizPage: React.FC = () => {
  return (
    <Layout title="Quiz | AI-Powered Learning Platform">
      <Quiz />
    </Layout>
  );
};

export default QuizPage;
