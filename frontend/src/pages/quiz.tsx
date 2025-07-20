import React, { useEffect, useState } from 'react';
import Layout from '@/components/layout';
import {
  Typography,
  Box,
  CircularProgress,
  Paper,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
} from '@mui/material';
import { generateQuiz, submitQuiz } from '@/api/quiz';
import { QuizQuestion } from '@/types/quiz';

const QuizPage: React.FC = () => {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [score, setScore] = useState<number | null>(null);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const quiz = await generateQuiz();
        setQuestions(quiz);
      } catch (error) {
        console.error('Error generating quiz:', error);
      } finally {
        setLoading(false);
      }
    };

    if (questions.length === 0) {
      fetchQuiz();
    } else {
      setLoading(false);
    }
  }, []); // run once on mount

  const handleChange = (questionId: number, optionIndex: number) => {
    setAnswers((prev) => ({ ...prev, [questionId]: optionIndex }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const result = await submitQuiz(answers);
      setScore(result.score);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Quiz | AI-Powered Learning Platform">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout title="Quiz | AI-Powered Learning Platform">
      <Typography variant="h4" component="h1" gutterBottom>
        Quiz
      </Typography>
      <form onSubmit={handleSubmit}>
        {questions.map((q) => (
          <Paper key={q.id} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              {q.question}
            </Typography>
            <RadioGroup
              value={answers[q.id] ?? ''}
              onChange={(e) => handleChange(q.id, parseInt(e.target.value, 10))}
            >
              {q.options.map((opt, idx) => (
                <FormControlLabel
                  key={idx}
                  value={idx}
                  control={<Radio />}
                  label={opt}
                />
              ))}
            </RadioGroup>
          </Paper>
        ))}
        {score !== null && (
          <Typography variant="h5" sx={{ mb: 2 }}>
            Your Score: {score}
          </Typography>
        )}
        <Button type="submit" variant="contained" color="primary" disabled={submitting}>
          {submitting ? <CircularProgress size={24} /> : 'Submit Quiz'}
        </Button>
      </form>
    </Layout>
  );
};

export default QuizPage;
