import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

export const register = async (username: string, email: string, password: string) => {
  const response = await api.post('/auth/register', { username, email, password });
  return response.data;
};

export const getLearningPath = async (userEmail: string, courseId: number) => {
  const response = await api.get(`/learning-path/${userEmail}/${courseId}`);
  return response.data;
};

export const getLesson = async (lessonId: number) => {
  const response = await api.get(`/lessons/${lessonId}`);
  return response.data;
};

export const submitAnswer = async (lessonId: number, userId: number, answer: string) => {
  const response = await api.post(`/lessons/${lessonId}/submit`, { userId, answer });
  return response.data;
};

export const getAudioLesson = async (topic: string, era: string) => {
  const response = await api.get(`/history/audio-lesson?topic=${topic}&era=${era}`);
  return response.data;
};

export const getScienceQuestion = async (topic: string, difficulty: string) => {
  const response = await api.get(`/science/question?topic=${topic}&difficulty=${difficulty}`);
  return response.data;
};

export const getScienceInfographic = async (topic: string) => {
  const response = await api.get(`/science/infographic?topic=${topic}`);
  return response.data;
};

export const getTechCodingChallenge = async (language: string, difficulty: string) => {
  const response = await api.get(`/tech/coding-challenge?language=${language}&difficulty=${difficulty}`);
  return response.data;
};

export const getUserCourses = async (userEmail: string) => {
  const response = await api.get(`/users/${userEmail}/courses`);
  return response.data;
};

export const getUserProgress = async (userEmail: string) => {
  const response = await api.get(`/users/${userEmail}/progress`);
  return response.data;
};

export const getUserProfile = async (email: string) => {
  const response = await api.get(`/users/profile/${email}`);
  return response.data;
};

export const updateUserProfile = async (email: string, profileData: any) => {
  const response = await api.put(`/users/profile/${email}`, profileData);
  return response.data;
};

export const getPersonalizedRecommendations = async (userEmail: string) => {
  const response = await api.get(`/personalized-recommendations/${userEmail}`);
  return response.data;
};

export const getWeb3Nonce = async (address: string, chain: number, network: string) => {
  const response = await api.post('/auth/web3nonce', { address, chain, network });
  return response.data;
};

export const verifyWeb3Signature = async (message: string, signature: string, address: string, chain: number, network: string) => {
  const response = await api.post('/auth/web3verify', { message, signature, address, chain, network });
  return response.data;
};

export const getUserAchievements = async (email: string) => {
  const response = await api.get(`/users/${email}/achievements`);
  return response.data;
};

export const getUserLevel = async (email: string) => {
  const response = await api.get(`/users/${email}/level`);
  return response.data;
};

export const completeLesson = async (lessonId: number, email: string) => {
  const response = await api.post(`/lessons/${lessonId}/complete`, { email });
  return response.data;
};

export const getDailyChallenge = async (email: string) => {
  const response = await api.get(`/users/${email}/daily-challenge`);
  return response.data;
};

export const completeDailyChallenge = async (email: string, challengeId: number) => {
  const response = await api.post(`/users/${email}/daily-challenge/${challengeId}/complete`);
  return response.data;
};

export const getUserLearningStreak = async (email: string) => {
  const response = await api.get(`/users/${email}/learning-streak`);
  return response.data;
};

export const getUserStats = async (email: string) => {
  const response = await api.get(`/users/${email}/stats`);
  return response.data;
};

export const getLeaderboard = async () => {
  const response = await api.get('/leaderboard');
  return response.data;
};

export default api;
