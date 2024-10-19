import React from 'react';
import Link from 'next/link';
import { Grid, Card, CardContent, CardActionArea, Typography } from '@mui/material';
import { Course } from '@/types/course';

interface CourseListProps {
  courses: Course[];
}

const CourseList: React.FC<CourseListProps> = ({ courses }) => {
  return (
    <Grid container spacing={4}>
      {courses.map((course) => (
        <Grid item key={course.id} xs={12} sm={6} md={4}>
          <Card>
            <CardActionArea component={Link} href={`/courses/${course.id}`}>
              <CardContent>
                <Typography gutterBottom variant="h5" component="div">
                  {course.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {course.description}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Type: {course.type}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Topic: {course.topic}
                </Typography>
                {course.difficulty && (
                  <Typography variant="body2" color="text.secondary">
                    Difficulty: {course.difficulty}
                  </Typography>
                )}
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default CourseList;
