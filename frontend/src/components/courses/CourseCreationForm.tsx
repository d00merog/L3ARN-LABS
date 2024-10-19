import React, { useState } from 'react';
import { useForm, Controller, FieldValues } from 'react-hook-form';
import { createCourse } from '@/api/courses';
import { TextField, Button, Select, MenuItem, FormControl, InputLabel, Box, Typography, Snackbar } from '@mui/material';
import { Alert } from '@mui/material';
import { useRouter } from 'next/router';

type CourseFormData = {
  title: string;
  description: string;
  type: 'language' | 'history';
  topic: string;
  difficulty?: string;
  era?: string;
  model: string;
};

const CourseCreationForm: React.FC = () => {
  const { control, handleSubmit, watch, formState: { errors } } = useForm<CourseFormData>();
  const [isLoading, setIsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const courseType = watch('type');
  const router = useRouter();

  const onSubmit = async (data: CourseFormData) => {
    setIsLoading(true);
    try {
      await createCourse(data);
      setSnackbar({ open: true, message: 'Course created successfully!', severity: 'success' });
      setTimeout(() => {
        router.push('/courses');
      }, 2000);
    } catch (error) {
      setSnackbar({ open: true, message: 'Failed to create course. Please try again.', severity: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ maxWidth: 600, margin: 'auto' }}>
      <Typography variant="h4" component="h2" gutterBottom>
        Create a New Course
      </Typography>
      <Controller
        name="title"
        control={control}
        rules={{ required: 'Title is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Course Title"
            fullWidth
            margin="normal"
            error={!!errors.title}
            helperText={errors.title?.message}
          />
        )}
      />
      <Controller
        name="description"
        control={control}
        rules={{ required: 'Description is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Course Description"
            fullWidth
            multiline
            rows={4}
            margin="normal"
            error={!!errors.description}
            helperText={errors.description?.message}
          />
        )}
      />
      <Controller
        name="type"
        control={control}
        rules={{ required: 'Type is required' }}
        render={({ field }) => (
          <FormControl fullWidth margin="normal">
            <InputLabel>Course Type</InputLabel>
            <Select
              {...field}
              error={!!errors.type}
            >
              <MenuItem value="language">Language</MenuItem>
              <MenuItem value="history">History</MenuItem>
            </Select>
          </FormControl>
        )}
      />
      <Controller
        name="topic"
        control={control}
        rules={{ required: 'Topic is required' }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Topic"
            fullWidth
            margin="normal"
            error={!!errors.topic}
            helperText={errors.topic?.message}
          />
        )}
      />
      {courseType === 'language' && (
        <Controller
          name="difficulty"
          control={control}
          rules={{ required: 'Difficulty is required for language courses' }}
          render={({ field }) => (
            <FormControl fullWidth margin="normal">
              <InputLabel>Difficulty</InputLabel>
              <Select
                {...field}
                error={!!errors.difficulty}
              >
                <MenuItem value="beginner">Beginner</MenuItem>
                <MenuItem value="intermediate">Intermediate</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </Select>
            </FormControl>
          )}
        />
      )}
      {courseType === 'history' && (
        <Controller
          name="era"
          control={control}
          rules={{ required: 'Era is required for history courses' }}
          render={({ field }) => (
            <TextField
              {...field}
              label="Historical Era"
              fullWidth
              margin="normal"
              error={!!errors.era}
              helperText={errors.era?.message}
            />
          )}
        />
      )}
      <Controller
        name="model"
        control={control}
        rules={{ required: 'Model is required' }}
        render={({ field }) => (
          <FormControl fullWidth margin="normal">
            <InputLabel>AI Model</InputLabel>
            <Select
              {...field}
              error={!!errors.model}
            >
              <MenuItem value="claude">Claude</MenuItem>
              <MenuItem value="openai">OpenAI</MenuItem>
              <MenuItem value="huggingface">HuggingFace</MenuItem>
              <MenuItem value="local">Local Model</MenuItem>
            </Select>
          </FormControl>
        )}
      />
      <Button
        type="submit"
        variant="contained"
        color="primary"
        fullWidth
        size="large"
        disabled={isLoading}
        sx={{ mt: 2 }}
      >
        {isLoading ? 'Creating...' : 'Create Course'}
      </Button>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CourseCreationForm;
