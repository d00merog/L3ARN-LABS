import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { motion } from 'framer-motion';

interface UserStatsProps {
  totalCoursesCompleted: number;
  totalLessonsCompleted: number;
  totalXPEarned: number;
  averageScore: number;
}

const UserStats: React.FC<UserStatsProps> = ({
  totalCoursesCompleted,
  totalLessonsCompleted,
  totalXPEarned,
  averageScore,
}) => {
  const stats = [
    { label: 'Courses Completed', value: totalCoursesCompleted },
    { label: 'Lessons Completed', value: totalLessonsCompleted },
    { label: 'Total XP Earned', value: totalXPEarned },
    { label: 'Average Score', value: `${averageScore.toFixed(1)}%` },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" gutterBottom>
        Your Learning Stats
      </Typography>
      <Grid container spacing={2}>
        {stats.map((stat, index) => (
          <Grid item xs={6} sm={3} key={index}>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Paper elevation={3} sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h4" component="div" color="primary">
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default UserStats;
