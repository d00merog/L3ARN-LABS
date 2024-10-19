import React, { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import { Typography, Box, TextField, Button, Avatar, Grid, Paper, CircularProgress, Snackbar, Alert, Tabs, Tab } from '@mui/material';
import { getUserProfile, updateUserProfile, getUserAchievements, getUserLevel } from '@/utils/api';
import UserAchievements from '@/components/user/UserAchievements';
import UserLevel from '@/components/user/UserLevel';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  bio: string;
  interests: string[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ProfilePage: React.FC = () => {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [achievements, setAchievements] = useState([]);
  const [userLevel, setUserLevel] = useState({ level: 1, xp: 0, xpToNextLevel: 100 });
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    } else if (status === 'authenticated' && session?.user?.email) {
      fetchUserProfile(session.user.email);
      fetchUserAchievements(session.user.email);
      fetchUserLevel(session.user.email);
    }
  }, [status, session, router]);

  const fetchUserProfile = async (email: string) => {
    try {
      const userProfile = await getUserProfile(email);
      setProfile(userProfile);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setSnackbar({ open: true, message: 'Failed to load profile. Please try again.', severity: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUserAchievements = async (email: string) => {
    try {
      const userAchievements = await getUserAchievements(email);
      setAchievements(userAchievements);
    } catch (error) {
      console.error('Error fetching user achievements:', error);
    }
  };

  const fetchUserLevel = async (email: string) => {
    try {
      const level = await getUserLevel(email);
      setUserLevel(level);
    } catch (error) {
      console.error('Error fetching user level:', error);
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (profile && session?.user?.email) {
      try {
        await updateUserProfile(session.user.email, profile);
        setIsEditing(false);
        setSnackbar({ open: true, message: 'Profile updated successfully!', severity: 'success' });
      } catch (error) {
        console.error('Error updating user profile:', error);
        setSnackbar({ open: true, message: 'Failed to update profile. Please try again.', severity: 'error' });
      }
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (status === 'loading' || isLoading) {
    return (
      <Layout title="Profile | AI-Powered Learning Platform">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  if (!profile) {
    return <Layout title="Profile | AI-Powered Learning Platform">Profile not found</Layout>;
  }

  return (
    <Layout title="Profile | AI-Powered Learning Platform">
      <Paper elevation={3} sx={{ p: 4, maxWidth: 800, margin: 'auto' }}>
        <Grid container spacing={3} alignItems="center" sx={{ mb: 4 }}>
          <Grid item>
            <Avatar
              alt={profile.name}
              src={session?.user?.image || ''}
              sx={{ width: 100, height: 100 }}
            />
          </Grid>
          <Grid item xs>
            <Typography variant="h4" component="h1" gutterBottom>
              {profile.name}
            </Typography>
            <Typography variant="body1" color="textSecondary">
              {profile.email}
            </Typography>
          </Grid>
        </Grid>
        <UserLevel level={userLevel.level} xp={userLevel.xp} xpToNextLevel={userLevel.xpToNextLevel} />
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="profile tabs">
          <Tab label="Profile" />
          <Tab label="Achievements" />
        </Tabs>
        <TabPanel value={tabValue} index={0}>
          <Box component="form" onSubmit={handleProfileUpdate} sx={{ mt: 4 }}>
            <TextField
              fullWidth
              label="Bio"
              multiline
              rows={4}
              value={profile.bio}
              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
              disabled={!isEditing}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Interests"
              value={profile.interests.join(', ')}
              onChange={(e) => setProfile({ ...profile, interests: e.target.value.split(',').map(i => i.trim()) })}
              disabled={!isEditing}
              margin="normal"
              helperText="Separate interests with commas"
            />
            {isEditing ? (
              <Box sx={{ mt: 2 }}>
                <Button type="submit" variant="contained" color="primary" sx={{ mr: 2 }}>
                  Save Changes
                </Button>
                <Button variant="outlined" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
              </Box>
            ) : (
              <Button variant="contained" color="primary" onClick={() => setIsEditing(true)} sx={{ mt: 2 }}>
                Edit Profile
              </Button>
            )}
          </Box>
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <UserAchievements achievements={achievements} />
        </TabPanel>
      </Paper>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Layout>
  );
};

export default ProfilePage;
