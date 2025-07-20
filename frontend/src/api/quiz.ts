import axios from 'axios';
import { QuizQuestion, QuizResult } from '@/types/quiz';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const getToken = () => {
  return localStorage.getItem('authToken') || '';
};

export const generateQuiz = async (): Promise<QuizQuestion[]> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/generate`, {}, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    // assume response.data.quiz is the questions array
    return response.data.quiz || response.data;
  } catch (error) {
    console.error('Error generating quiz:', error);
    throw error;
  }
};

export const submitQuiz = async (answers: Record<number, number>): Promise<QuizResult> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/submit`, { answers }, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting quiz:', error);
    throw error;
  }
};
