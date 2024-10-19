import React from 'react';
import { Typography, Box, Chip, Button } from '@mui/material';
import { Course } from '@/types/course';

interface CourseDetailsProps {
  course: Course;
  onEnroll: () => void;
}

const CourseDetails: React.FC<CourseDetailsProps> = ({ course, onEnroll }) => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {course.title}
      </Typography>
      <Typography variant="body1" paragraph>
        {course.description}
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip label={`Type: ${course.type}`} />
        <Chip label={`Topic: ${course.topic}`} />
        {course.difficulty && <Chip label={`Difficulty: ${course.difficulty}`} />}
        {course.era && <Chip label={`Era: ${course.era}`} />}
      </Box>
      <Typography variant="body2" color="text.secondary" paragraph>
        Model: {course.model}
      </Typography>
      <Button variant="contained" color="primary" onClick={onEnroll}>
        Enroll in Course
      </Button>
    </Box>
  );
};

export default CourseDetails;
