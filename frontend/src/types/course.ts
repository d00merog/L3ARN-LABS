export interface Lesson {
  id: number;
  title: string;
  description: string;
  content: string;
  order: number;
  difficulty: string;
  course_id: number;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  type: string;
  topic: string;
  difficulty?: string;
  era?: string;
  model: string;
  instructor_id: number;
  created_at: string;
  updated_at: string;
}
