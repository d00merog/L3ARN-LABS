import React from 'react';
import { Card, CardContent, Typography, Box, Tooltip } from '@mui/material';
import { motion } from 'framer-motion';

interface AchievementCardProps {
  title: string;
  description: string;
  icon: string;
  date: string;
}

const AchievementCard: React.FC<AchievementCardProps> = ({ title, description, icon, date }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <img src={icon} alt={title} style={{ width: 64, height: 64 }} />
          </Box>
          <Tooltip title={description} arrow>
            <Typography gutterBottom variant="h6" component="div" align="center">
              {title}
            </Typography>
          </Tooltip>
          <Typography variant="body2" color="text.secondary" align="center">
            Achieved on: {new Date(date).toLocaleDateString()}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default AchievementCard;
