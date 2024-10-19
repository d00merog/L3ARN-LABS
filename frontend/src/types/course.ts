export interface Course {
  id: number;
  title: string;
  description: string;
  type: string;
  topic: string;
  difficulty?: string;
  era?: string;
  model: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}
