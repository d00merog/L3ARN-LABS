import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/layout';
import { Typography, Grid, Card, CardContent, Button, Box, CircularProgress, Tabs, Tab, Fade, Grow } from '@mui/material';
import { motion } from 'framer-motion';
import { getUserCourses, getUserProgress, getUserLevel, getUserAchievements, getUserLearningStreak, getUserStats, getLeaderboard } from '@/api/user';
import CourseOverview from '@/components/courses/CourseOverview';
import UserProgress from '@/components/dashboard/UserProgress';
import UserLevel from '@/components/user/UserLevel';
import UserAchievements from '@/components/user/UserAchievements';
import { UserProgress as UserProgressType, UserLevel as UserLevelType, UserAchievement, UserStats as UserStatsType, LeaderboardEntry } from '@/types/user';
import CourseRecommendations from '@/components/courses/CourseRecommendations';
import { useSession } from 'next-auth/react';
import DailyChallenge from '@/components/gamification/DailyChallenge';
import LearningStreakComponent from '@/components/user/LearningStreak';
import UserStatsComponent from '@/components/user/UserStats';
import Leaderboard from '@/components/leaderboard/Leaderboard';

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

interface Course {
  id: number;
  title: string;
  description: string;
}

interface LearningStreak {
  currentStreak: number;
  longestStreak: number;
}

const Dashboard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const router = useRouter();
  const [userCourses, setUserCourses] = useState<Course[]>([]);
  const [userProgress, setUserProgress] = useState<UserProgressType[]>([]);
  const [userLevel, setUserLevel] = useState<UserLevelType>({ level: 1, xp: 0, xpToNextLevel: 100 });
  const [userAchievements, setUserAchievements] = useState<UserAchievement[]>([]);
  const [learningStreak, setLearningStreak] = useState<LearningStreak>({ currentStreak: 0, longestStreak: 0 });
  const [userStats, setUserStats] = useState<UserStatsType>({
    totalCoursesCompleted: 0,
    totalLessonsCompleted: 0,
    totalXPEarned: 0,
    averageScore: 0,
  });
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const { data: session, status } = useSession();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      if (status === 'authenticated') {
        try {
          const courses = await getUserCourses();
          setUserCourses(courses);
          const progress = await getUserProgress();
          setUserProgress(progress);
          const level = await getUserLevel();
          setUserLevel(level);
          const achievements = await getUserAchievements();
          setUserAchievements(achievements);
          const streak = await getUserLearningStreak();
          setLearningStreak(streak);
          const stats = await getUserStats();
          setUserStats(stats);
          const leaderboardData = await getLeaderboard();
          setLeaderboard(leaderboardData);
        } catch (error) {
          console.error('Error fetching data:', error);
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchData();
  }, [status]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (status === 'loading' || isLoading) {
    return (
      <Layout title="Dashboard | AI-Powered Learning Platform">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  if (status === 'unauthenticated') {
    router.push('/login');
    return null;
  }

  return (
    <Layout title="Dashboard | AI-Powered Learning Platform">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <Typography variant="h3" component="h1" gutterBottom>
            Your Learning Dashboard
          </Typography>
        </motion.div>
        <motion.div variants={itemVariants}>
          <UserLevel level={userLevel.level} xp={userLevel.xp} xpToNextLevel={userLevel.xpToNextLevel} />
        </motion.div>
        <motion.div variants={itemVariants}>
          <LearningStreakComponent currentStreak={learningStreak.currentStreak} longestStreak={learningStreak.longestStreak} />
        </motion.div>
        <motion.div variants={itemVariants}>
          <UserStatsComponent {...userStats} />
        </motion.div>
        <motion.div variants={itemVariants}>
          <DailyChallenge userEmail={session?.user?.email || ''} />
        </motion.div>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tab label="Overview" />
            <Tab label="My Courses" />
            <Tab label="Recommendations" />
            <Tab label="Achievements" />
            <Tab label="Interactive Lessons" />
            <Tab label="Leaderboard" />
          </Tabs>
        </Box>
        <Fade in={tabValue === 0}>
          <TabPanel value={tabValue} index={0}>
            <UserProgress courses={userProgress.map(progress => ({
              courseId: progress.courseId,
              courseTitle: progress.courseTitle,
              completedLessons: progress.completedLessons,
              totalLessons: progress.totalLessons
            }))} />
          </TabPanel>
        </Fade>
        <Fade in={tabValue === 1}>
          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={4}>
              {userCourses.map((course, index) => (
                <Grow
                  in={tabValue === 1}
                  style={{ transformOrigin: '0 0 0' }}
                  {...(tabValue === 1 ? { timeout: 1000 + index * 500 } : {})}
                  key={course.id}
                >
                  <Grid item xs={12} sm={6} md={4}>
                    <Card>
                      <CardContent>
                        <Typography variant="h5" component="div" gutterBottom>
                          {course.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {course.description}
                        </Typography>
                        <Button
                          variant="contained"
                          color="primary"
                          onClick={() => router.push(`/courses/${course.id}`)}
                          sx={{ mt: 2 }}
                        >
                          Continue Learning
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grow>
              ))}
            </Grid>
          </TabPanel>
        </Fade>
        <Fade in={tabValue === 2}>
          <TabPanel value={tabValue} index={2}>
            <CourseRecommendations userId={session?.user?.email || ''} />
          </TabPanel>
        </Fade>
        <Fade in={tabValue === 3}>
          <TabPanel value={tabValue} index={3}>
            <UserAchievements achievements={userAchievements} />
          </TabPanel>
        </Fade>
        <Fade in={tabValue === 4}>
          <TabPanel value={tabValue} index={4}>
            <Typography variant="h5" component="h2" gutterBottom>
              Interactive Lessons
            </Typography>
            <Typography variant="body1">
              This section is under development. Check back soon for interactive lessons!
            </Typography>
          </TabPanel>
        </Fade>
        <Fade in={tabValue === 5}>
          <TabPanel value={tabValue} index={5}>
            <Leaderboard entries={leaderboard.map((entry, index) => ({
              ...entry,
              rank: index + 1
            }))} />
          </TabPanel>
        </Fade>
      </motion.div>
    </Layout>
  );
};

export default Dashboard;
