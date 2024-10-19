import React from 'react';
import { Typography, Box, LinearProgress, Grid, Paper } from '@mui/material';

interface CourseProgress {
  courseId: number;
  courseTitle: string;
  completedLessons: number;
  totalLessons: number;
}

interface UserProgressProps {
  courses: CourseProgress[];
}

const UserProgress: React.FC<UserProgressProps> = ({ courses }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>Your Progress</Typography>
      <Grid container spacing={2}>
        {courses.map((course) => (
          <Grid item xs={12} key={course.courseId}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="subtitle1">{course.courseTitle}</Typography>
              <Box display="flex" alignItems="center">
                <Box width="100%" mr={1}>
                  <LinearProgress
                    variant="determinate"
                    value={(course.completedLessons / course.totalLessons) * 100}
                  />
                </Box>
                <Box minWidth={35}>
                  <Typography variant="body2" color="textSecondary">
                    {`${Math.round((course.completedLessons / course.totalLessons) * 100)}%`}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary">
                {`${course.completedLessons} of ${course.totalLessons} lessons completed`}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default UserProgress;
