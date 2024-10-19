import axios, { AxiosError } from 'axios';
import { Course } from '@/types/course';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const getToken = () => {
  // Implement token retrieval logic here
  // For example, you could retrieve it from localStorage or a state management solution
  return localStorage.getItem('authToken') || '';
};

export const createCourse = async (courseData: Omit<Course, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/courses/`, courseData, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error creating course:', error.response?.data || error.message);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
};

export const getCourse = async (courseId: string): Promise<Course> => {
  try {
    const response = await axios.get<Course>(`${API_BASE_URL}/api/courses/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      console.error('Error fetching course:', error.response?.data);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
};

export const updateCourse = async (courseId: string, courseData: Partial<Course>): Promise<Course> => {
  try {
    const response = await axios.put<Course>(`${API_BASE_URL}/api/courses/${courseId}`, courseData, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      console.error('Error updating course:', error.response?.data);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
};

export const deleteCourse = async (courseId: string): Promise<void> => {
  try {
    await axios.delete(`${API_BASE_URL}/api/courses/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
  } catch (error) {
    if (error instanceof AxiosError) {
      console.error('Error deleting course:', error.response?.data);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
};

export const getAllCourses = async (): Promise<Course[]> => {
  try {
    const response = await axios.get<Course[]>(`${API_BASE_URL}/api/courses/`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error fetching all courses:', error.response?.data);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
};

export const enrollInCourse = async (courseId: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/courses/${courseId}/enroll`, {}, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      console.error('Error enrolling in course:', error.response?.data);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
};
