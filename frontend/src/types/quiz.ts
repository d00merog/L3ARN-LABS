export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
}

export interface QuizResult {
  score: number;
}
