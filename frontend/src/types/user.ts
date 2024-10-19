export interface User {
  id: string;
  name?: string | null;
  email?: string | null;
  image?: string | null;
}

export interface UserProgress {
  courseId: number;
  courseTitle: string;
  progress: number;
  completedLessons: number;
  totalLessons: number;
}

export interface UserLevel {
  level: number;
  xp: number;
  xpToNextLevel: number;
}

export interface UserAchievement {
  id: number;
  title: string;
  description: string;
  date: string;
  icon: string;
}

export interface LearningStreak {
  currentStreak: number;
  longestStreak: number;
}

export interface UserStats {
  totalCoursesCompleted: number;
  totalLessonsCompleted: number;
  totalXPEarned: number;
  averageScore: number;
}

export interface LeaderboardEntry {
  userId: string;
  username: string;
  xp: number;
  level: number;
}
