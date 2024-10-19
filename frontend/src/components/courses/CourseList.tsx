import React from 'react';
import Link from 'next/link';
import { Course } from '@/types/course';

interface CourseListProps {
  courses: Course[];
}

const CourseList: React.FC<CourseListProps> = ({ courses }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {courses.map((course) => (
        <div key={course.id} className="border rounded-lg p-4 shadow-md">
          <h2 className="text-xl font-semibold mb-2">{course.title}</h2>
          <p className="text-gray-600 mb-4">{course.description}</p>
          <Link href={`/courses/${course.id}`} className="text-blue-500 hover:underline">
            View Course
          </Link>
        </div>
      ))}
    </div>
  );
};

export default CourseList;
