import React, { useState, useEffect } from 'react';
import { Typography, Box, Rating, TextField, Button, List, ListItem, Divider } from '@mui/material';
import api from '@/utils/api';

interface Review {
  id: number;
  user: string;
  rating: number;
  comment: string;
  createdAt: string;
}

interface CourseReviewsProps {
  courseId: number;
}

const CourseReviews: React.FC<CourseReviewsProps> = ({ courseId }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [newReview, setNewReview] = useState({ rating: 0, comment: '' });

  useEffect(() => {
    fetchReviews();
  }, [courseId]);

  const fetchReviews = async () => {
    try {
      const response = await api.get(`/courses/${courseId}/reviews`);
      setReviews(response.data);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post(`/courses/${courseId}/reviews`, newReview);
      setNewReview({ rating: 0, comment: '' });
      fetchReviews();
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  return (
    <Box mt={4}>
      <Typography variant="h5" gutterBottom>Course Reviews</Typography>
      <List>
        {reviews.map((review) => (
          <React.Fragment key={review.id}>
            <ListItem>
              <Box>
                <Typography variant="subtitle1">{review.user}</Typography>
                <Rating value={review.rating} readOnly />
                <Typography variant="body1">{review.comment}</Typography>
                <Typography variant="caption">{new Date(review.createdAt).toLocaleDateString()}</Typography>
              </Box>
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>
      <Box component="form" onSubmit={handleSubmitReview} mt={2}>
        <Typography variant="h6">Write a Review</Typography>
        <Rating
          value={newReview.rating}
          onChange={(_, value) => setNewReview({ ...newReview, rating: value || 0 })}
        />
        <TextField
          fullWidth
          multiline
          rows={4}
          variant="outlined"
          placeholder="Your review"
          value={newReview.comment}
          onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
          margin="normal"
        />
        <Button type="submit" variant="contained" color="primary">
          Submit Review
        </Button>
      </Box>
    </Box>
  );
};

export default CourseReviews;
