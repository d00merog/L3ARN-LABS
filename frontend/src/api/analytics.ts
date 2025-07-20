import axios from 'axios';
import { LessonAnalytics } from '@/types/analytics';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const getToken = () => {
  return localStorage.getItem('authToken') || '';
};

export const getInstructorAnalytics = async (): Promise<LessonAnalytics[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/analytics/instructor/analytics`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching instructor analytics:', error);
    throw error;
  }
};
