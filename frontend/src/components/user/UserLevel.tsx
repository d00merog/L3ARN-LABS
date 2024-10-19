import React from 'react';
import { Box, Typography, LinearProgress, Tooltip } from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';

interface UserLevelProps {
  level: number;
  xp: number;
  xpToNextLevel: number;
}

const UserLevel: React.FC<UserLevelProps> = ({ level, xp, xpToNextLevel }) => {
  const progress = (xp / xpToNextLevel) * 100;

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <EmojiEventsIcon color="primary" sx={{ mr: 1 }} />
        <Typography variant="h6">Level {level}</Typography>
      </Box>
      <Tooltip title={`${xp}/${xpToNextLevel} XP`} arrow>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 10, borderRadius: 5 }} />
      </Tooltip>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        {xp} / {xpToNextLevel} XP to next level
      </Typography>
    </Box>
  );
};

export default UserLevel;
