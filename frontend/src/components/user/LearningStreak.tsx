import React from 'react';
import { Box, Typography, LinearProgress, Tooltip } from '@mui/material';
import WhatshotIcon from '@mui/icons-material/Whatshot';

interface LearningStreakProps {
  currentStreak: number;
  longestStreak: number;
}

const LearningStreak: React.FC<LearningStreakProps> = ({ currentStreak, longestStreak }) => {
  const progress = (currentStreak / longestStreak) * 100;

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <WhatshotIcon color="error" sx={{ mr: 1 }} />
        <Typography variant="h6">Learning Streak</Typography>
      </Box>
      <Tooltip title={`${currentStreak} days`} arrow>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 5 }} />
      </Tooltip>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Current Streak: {currentStreak} days
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Longest Streak: {longestStreak} days
        </Typography>
      </Box>
    </Box>
  );
};

export default LearningStreak;
