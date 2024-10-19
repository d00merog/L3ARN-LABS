import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { motion } from 'framer-motion';

interface CourseProgressProps {
  completedLessons: number;
  totalLessons: number;
}

const CourseProgress: React.FC<CourseProgressProps> = ({ completedLessons, totalLessons }) => {
  const progress = (completedLessons / totalLessons) * 100;

  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Course Progress
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {completedLessons} / {totalLessons} lessons completed
        </Typography>
      </Box>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: '100%' }}
        transition={{ duration: 0.5 }}
      >
        <LinearProgress variant="determinate" value={progress} />
      </motion.div>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {Math.round(progress)}% Complete
        </Typography>
      </motion.div>
    </Box>
  );
};

export default CourseProgress;
