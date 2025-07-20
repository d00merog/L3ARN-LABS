import React, { useEffect, useState } from 'react';
import Layout from '@/components/layout';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Box, CircularProgress } from '@mui/material';
import { getInstructorAnalytics } from '@/api/analytics';
import { LessonAnalytics } from '@/types/analytics';

const InstructorDashboard: React.FC = () => {
  const [data, setData] = useState<LessonAnalytics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const analytics = await getInstructorAnalytics();
        setData(analytics);
      } catch (error) {
        console.error('Failed to load analytics', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout title="Instructor Dashboard | AI-Powered Learning Platform">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout title="Instructor Dashboard | AI-Powered Learning Platform">
      <Typography variant="h4" gutterBottom>
        Lesson Analytics
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Lesson</TableCell>
              <TableCell align="right">Avg Score</TableCell>
              <TableCell align="right">#Attempts</TableCell>
              <TableCell align="right">Last Activity</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, index) => (
              <TableRow key={index}>
                <TableCell component="th" scope="row">
                  {row.lessonTitle}
                </TableCell>
                <TableCell align="right">{row.avgScore}</TableCell>
                <TableCell align="right">{row.attempts}</TableCell>
                <TableCell align="right">{row.lastActivity}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Layout>
  );
};

export default InstructorDashboard;
