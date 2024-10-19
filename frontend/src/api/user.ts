import axios from 'axios';
import { Course } from '@/types/course';
import { UserProgress, UserLevel, UserAchievement, LearningStreak, UserStats, LeaderboardEntry } from '@/types/user';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const getToken = () => {
  return localStorage.getItem('authToken') || '';
};

export const getUserCourses = async (): Promise<Course[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/me/courses`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user courses:', error);
    throw error;
  }
};

export const getUserProgress = async (): Promise<UserProgress[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/me/progress`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user progress:', error);
    throw error;
  }
};

export const getUserLevel = async (): Promise<UserLevel> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/me/level`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user level:', error);
    throw error;
  }
};

export const getUserAchievements = async (): Promise<UserAchievement[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/me/achievements`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user achievements:', error);
    throw error;
  }
};

export const getUserLearningStreak = async (): Promise<LearningStreak> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/me/learning-streak`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user learning streak:', error);
    throw error;
  }
};

export const getUserStats = async (): Promise<UserStats> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/users/me/stats`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user stats:', error);
    throw error;
  }
};

export const getLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/leaderboard`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    throw error;
  }
};
