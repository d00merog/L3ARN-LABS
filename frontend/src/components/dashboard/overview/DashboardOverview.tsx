import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  User, Book, Code, Trophy, TrendingUp, Clock,
  Brain, Network, Coins, MonitorSpeaker, Zap, Users
} from 'lucide-react';

interface DashboardStats {
  totalCourses: number;
  completedCourses: number;
  codeExecutions: number;
  taoEarned: number;
  learningStreak: number;
  totalStudyHours: number;
  aiInteractions: number;
  validationsCompleted: number;
}

interface RecentActivity {
  id: string;
  type: 'course_completed' | 'code_executed' | 'tao_earned' | 'validation';
  title: string;
  description: string;
  timestamp: string;
  icon: React.ElementType;
  color: string;
}

const DashboardOverview: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalCourses: 0,
    completedCourses: 0,
    codeExecutions: 0,
    taoEarned: 0,
    learningStreak: 0,
    totalStudyHours: 0,
    aiInteractions: 0,
    validationsCompleted: 0
  });

  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        totalCourses: 12,
        completedCourses: 8,
        codeExecutions: 247,
        taoEarned: 15.42,
        learningStreak: 7,
        totalStudyHours: 156.5,
        aiInteractions: 89,
        validationsCompleted: 23
      });

      setRecentActivities([
        {
          id: '1',
          type: 'course_completed',
          title: 'Advanced Python Programming',
          description: 'Completed with 95% score',
          timestamp: '2 hours ago',
          icon: Book,
          color: 'text-green-400'
        },
        {
          id: '2',
          type: 'tao_earned',
          title: 'TAO Reward',
          description: 'Earned 0.5 TAO for code validation',
          timestamp: '4 hours ago',
          icon: Coins,
          color: 'text-yellow-400'
        },
        {
          id: '3',
          type: 'code_executed',
          title: 'WebVM Session',
          description: 'Successfully executed ML model training',
          timestamp: '6 hours ago',
          icon: Code,
          color: 'text-blue-400'
        },
        {
          id: '4',
          type: 'validation',
          title: 'Bittensor Validation',
          description: 'Participated in educational content validation',
          timestamp: '1 day ago',
          icon: Network,
          color: 'text-purple-400'
        }
      ]);

      setLoading(false);
    };

    loadDashboardData();
  }, []);

  const statCards = [
    {
      title: 'Courses Completed',
      value: `${stats.completedCourses}/${stats.totalCourses}`,
      icon: Book,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      change: '+2 this week',
      changeType: 'positive' as const
    },
    {
      title: 'Code Executions',
      value: stats.codeExecutions.toLocaleString(),
      icon: Code,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      change: '+34 today',
      changeType: 'positive' as const
    },
    {
      title: 'TAO Earned',
      value: stats.taoEarned.toFixed(2),
      icon: Coins,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
      change: '+1.2 this week',
      changeType: 'positive' as const
    },
    {
      title: 'Learning Streak',
      value: `${stats.learningStreak} days`,
      icon: Zap,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10',
      change: 'Keep it up!',
      changeType: 'positive' as const
    },
    {
      title: 'Study Hours',
      value: `${stats.totalStudyHours.toFixed(1)}h`,
      icon: Clock,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      change: '+12h this week',
      changeType: 'positive' as const
    },
    {
      title: 'AI Interactions',
      value: stats.aiInteractions.toString(),
      icon: Brain,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      change: '+15 today',
      changeType: 'positive' as const
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, <span className="text-cyan-400">Scholar</span>! 🎓
          </h1>
          <p className="text-gray-400">
            Here's your learning progress and recent activities
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.title}
              className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`${stat.bgColor} ${stat.color} w-12 h-12 rounded-xl flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6" />
                </div>
                <div className={`text-sm ${stat.changeType === 'positive' ? 'text-green-400' : 'text-red-400'}`}>
                  {stat.change}
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
              <p className="text-gray-400 text-sm">{stat.title}</p>
            </motion.div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <motion.div
            className="lg:col-span-2 bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-6 h-6 text-green-400" />
              <h2 className="text-xl font-bold">Recent Activity</h2>
            </div>
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <motion.div
                  key={activity.id}
                  className="flex items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
                >
                  <div className={`${activity.color} w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center`}>
                    <activity.icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{activity.title}</h3>
                    <p className="text-gray-400 text-sm">{activity.description}</p>
                  </div>
                  <span className="text-gray-500 text-sm">{activity.timestamp}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Quick Actions & Progress */}
          <motion.div
            className="space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {/* Quick Actions */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Quick Actions
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 p-3 rounded-xl transition-colors text-sm font-medium">
                  Start WebVM
                </button>
                <button className="bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 p-3 rounded-xl transition-colors text-sm font-medium">
                  Join Network
                </button>
                <button className="bg-green-500/20 hover:bg-green-500/30 text-green-400 p-3 rounded-xl transition-colors text-sm font-medium">
                  New Course
                </button>
                <button className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 p-3 rounded-xl transition-colors text-sm font-medium">
                  View Rewards
                </button>
              </div>
            </div>

            {/* Learning Progress */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-gold-400" />
                Learning Progress
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Course Completion</span>
                    <span className="text-blue-400">{Math.round((stats.completedCourses / stats.totalCourses) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-700"
                      style={{ width: `${(stats.completedCourses / stats.totalCourses) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Weekly Goal</span>
                    <span className="text-green-400">78%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all duration-700 w-3/4"></div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;