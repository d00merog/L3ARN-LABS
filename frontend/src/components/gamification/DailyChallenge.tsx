import React, { useState, useEffect } from 'react';
import { Typography, Box, Button, CircularProgress, Paper, Fade } from '@mui/material';
import { motion } from 'framer-motion';
import { getDailyChallenge, completeDailyChallenge } from '@/utils/api';

interface DailyChallengeProps {
  userEmail: string;
}

const DailyChallenge: React.FC<DailyChallengeProps> = ({ userEmail }) => {
  const [challenge, setChallenge] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    fetchDailyChallenge();
  }, [userEmail]);

  const fetchDailyChallenge = async () => {
    try {
      const data = await getDailyChallenge(userEmail);
      setChallenge(data);
    } catch (error) {
      console.error('Error fetching daily challenge:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompleteChallenge = async () => {
    setIsCompleting(true);
    try {
      await completeDailyChallenge(userEmail, challenge.id);
      // Refresh the challenge after completion
      fetchDailyChallenge();
    } catch (error) {
      console.error('Error completing daily challenge:', error);
    } finally {
      setIsCompleting(false);
    }
  };

  if (isLoading) {
    return <CircularProgress />;
  }

  if (!challenge) {
    return <Typography>No daily challenge available.</Typography>;
  }

  return (
    <Fade in={true}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h5" gutterBottom>Daily Challenge</Typography>
          <Typography variant="body1" paragraph>{challenge.description}</Typography>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2">Reward: {challenge.xp_reward} XP</Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleCompleteChallenge}
              disabled={isCompleting}
            >
              {isCompleting ? <CircularProgress size={24} /> : 'Complete Challenge'}
            </Button>
          </Box>
        </motion.div>
      </Paper>
    </Fade>
  );
};

export default DailyChallenge;
