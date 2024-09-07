import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Lesson {
  id: number;
  title: string;
  content: string;
}

interface LessonViewerProps {
  lessonId: number;
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lessonId }) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLesson = async () => {
      try {
        const response = await axios.get(`/api/lessons/${lessonId}`);
        setLesson(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load lesson');
        setLoading(false);
      }
    };

    fetchLesson();
  }, [lessonId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!lesson) return <div>No lesson found</div>;

  return (
    <div>
      <h2>{lesson.title}</h2>
      <div dangerouslySetInnerHTML={{ __html: lesson.content }} />
    </div>
  );
};

export default LessonViewer;