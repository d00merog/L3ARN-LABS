import axios from 'axios';
import { Lesson } from '@/types/course';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const getToken = () => {
  return localStorage.getItem('authToken') || '';
};

export const getLesson = async (lessonId: number): Promise<Lesson> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/lessons/${lessonId}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching lesson:', error);
    throw error;
  }
};

export const getAudioLesson = async (topic: string, era: string): Promise<{ audio_url: string }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/lessons/audio`, {
      params: { topic, era },
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching audio lesson:', error);
    throw error;
  }
};

export const getScienceQuestion = async (subject: string, difficulty: string): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/lessons/science-question`, {
      params: { subject, difficulty },
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching science question:', error);
    throw error;
  }
};

export const getScienceInfographic = async (topic: string): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/lessons/science-infographic`, {
      params: { topic },
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching science infographic:', error);
    throw error;
  }
};

export const getTechCodingChallenge = async (language: string, difficulty: string): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/lessons/coding-challenge`, {
      params: { language, difficulty },
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching coding challenge:', error);
    throw error;
  }
};
