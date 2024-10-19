import React from 'react';
import { Box, Typography, Grid } from '@mui/material';
import AchievementCard from './AchievementCard';

interface Achievement {
  id: number;
  title: string;
  description: string;
  date: string;
  icon: string;
}

interface UserAchievementsProps {
  achievements: Achievement[];
}

const UserAchievements: React.FC<UserAchievementsProps> = ({ achievements }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Your Achievements
      </Typography>
      <Grid container spacing={3}>
        {achievements.map((achievement) => (
          <Grid item xs={12} sm={6} md={4} key={achievement.id}>
            <AchievementCard
              title={achievement.title}
              description={achievement.description}
              icon={achievement.icon}
              date={achievement.date}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default UserAchievements;
