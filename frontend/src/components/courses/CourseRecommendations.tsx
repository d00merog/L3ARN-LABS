import React, { useState, useEffect } from 'react';
import { Typography, Grid, Card, CardContent, CardMedia, CardActionArea } from '@mui/material';
import { useRouter } from 'next/router';
import { getPersonalizedRecommendations } from '@/utils/api';

interface Recommendation {
  course_id: number;
  title: string;
  probability: number;
}

const CourseRecommendations: React.FC<{ userId: string }> = ({ userId }) => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const router = useRouter();

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const data = await getPersonalizedRecommendations(userId);
        setRecommendations(data.recommendations);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      }
    };

    if (userId) {
      fetchRecommendations();
    }
  }, [userId]);

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Recommended Courses
      </Typography>
      <Grid container spacing={3}>
        {recommendations.map((recommendation) => (
          <Grid item key={recommendation.course_id} xs={12} sm={6} md={4}>
            <Card>
              <CardActionArea onClick={() => router.push(`/courses/${recommendation.course_id}`)}>
                <CardMedia
                  component="img"
                  height="140"
                  image={`https://source.unsplash.com/random?${recommendation.title}`}
                  alt={recommendation.title}
                />
                <CardContent>
                  <Typography gutterBottom variant="h6" component="div">
                    {recommendation.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Match: {Math.round(recommendation.probability * 100)}%
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default CourseRecommendations;
