import React from 'react';
import { useEffect, useState } from 'react';
import Layout from '../components/layout';
import CourseList from '../components/course/course-list';
import UserProfile from '../components/user/user-profile';
import RecentActivity from '../components/activity/recent-activity';
import UpcomingLessons from '../components/lessons/upcoming-lessons';
import ProgressSummary from '../components/progress/progress-summary';
import { useAuth } from '../contexts/auth-context';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [upcomingLessons, setUpcomingLessons] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch additional data needed for the dashboard
        const activityResponse = await fetch(`/api/users/${user?.id}/recent-activity`);
        const lessonsResponse = await fetch(`/api/users/${user?.id}/upcoming-lessons`);

        if (!activityResponse.ok || !lessonsResponse.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const activityData = await activityResponse.json();
        const lessonsData = await lessonsResponse.json();

        setRecentActivity(activityData);
        setUpcomingLessons(lessonsData);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
        setIsLoading(false);
      }
    };

    if (user?.id) {
      fetchDashboardData();
    }
  }, [user?.id]);

  if (isLoading) {
    return (
      <Layout title="Dashboard | Education Platform">
        <div>Loading dashboard...</div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Dashboard | Education Platform">
        <div>Error: {error}</div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard | Education Platform">
      <h1 className="text-3xl font-bold mb-6">Your Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <UserProfile userId={user?.id} />
        <ProgressSummary userId={user?.id} />
      </div>
      <h2 className="text-2xl font-semibold mt-8 mb-4">Your Courses</h2>
      <CourseList userId={user?.id} />
      <h2 className="text-2xl font-semibold mt-8 mb-4">Upcoming Lessons</h2>
      <UpcomingLessons lessons={upcomingLessons} />
      <h2 className="text-2xl font-semibold mt-8 mb-4">Recent Activity</h2>
      <RecentActivity activities={recentActivity} />
    </Layout>
  );
};

export default Dashboard;