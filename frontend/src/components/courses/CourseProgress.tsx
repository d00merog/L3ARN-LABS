import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

interface CourseProgressProps {
  courseId: number;
  userId: number;
}

const CourseProgress: React.FC<CourseProgressProps> = ({ courseId, userId }) => {
  const [progress, setProgress] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await api.get(`/courses/${courseId}/progress/${userId}`);
        setProgress(response.data.progress);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching course progress:', error);
        setIsLoading(false);
      }
    };

    fetchProgress();
  }, [courseId, userId]);

  if (isLoading) {
    return <div>Loading progress...</div>;
  }

  return (
    <div className="mt-4">
      <h3 className="text-lg font-semibold mb-2">Course Progress</h3>
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div
          className="bg-blue-600 h-2.5 rounded-full"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="mt-2">{progress}% complete</p>
    </div>
  );
};

export default CourseProgress;
