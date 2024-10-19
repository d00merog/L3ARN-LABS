import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/layout';
import { Typography, Grid, Card, CardContent, CardMedia, CardActionArea, TextField, InputAdornment, Button, Box } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { getCourses } from '@/api/courses';
import { useSession } from 'next-auth/react';
import { Course } from '@/types/course';

const CoursesPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const fetchedCourses = await getCourses();
        setCourses(fetchedCourses);
        setFilteredCourses(fetchedCourses);
      } catch (error) {
        console.error('Error fetching courses:', error);
        setError('Failed to load courses. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (status !== 'loading') {
      fetchCourses();
    }
  }, [status]);

  useEffect(() => {
    const filtered = courses.filter(course =>
      course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      course.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCourses(filtered);
  }, [searchTerm, courses]);

  const handleCreateCourse = () => {
    router.push('/courses/create');
  };

  if (status === 'loading' || isLoading) {
    return <Layout title="Courses | AI-Powered Learning Platform">Loading...</Layout>;
  }

  return (
    <Layout title="Courses | AI-Powered Learning Platform">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h3" component="h1">
          Explore Our Courses
        </Typography>
        {session && (
          <Button variant="contained" color="primary" onClick={handleCreateCourse}>
            Create Course
          </Button>
        )}
      </Box>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search courses..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 4 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
      {error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <Grid container spacing={4}>
          {filteredCourses.map((course) => (
            <Grid item key={course.id} xs={12} sm={6} md={4}>
              <Card>
                <CardActionArea onClick={() => router.push(`/courses/${course.id}`)}>
                  <CardMedia
                    component="img"
                    height="140"
                    image={`https://source.unsplash.com/random?${course.title}`}
                    alt={course.title}
                  />
                  <CardContent>
                    <Typography gutterBottom variant="h5" component="div">
                      {course.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {course.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Layout>
  );
};

export default CoursesPage;
