import React, { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import api from '@/utils/api';
import Button from '@/components/common/button';

interface Review {
  id: number;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  createdAt: string;
}

interface CourseReviewsProps {
  courseId: number;
}

const CourseReviews: React.FC<CourseReviewsProps> = ({ courseId }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [userRating, setUserRating] = useState(0);
  const [userComment, setUserComment] = useState('');
  const { data: session } = useSession();

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
    if (!session?.user) return;

    try {
      await api.post(`/courses/${courseId}/reviews`, {
        userId: (session.user as any).id, // Type assertion
        rating: userRating,
        comment: userComment,
      });
      setUserRating(0);
      setUserComment('');
      fetchReviews();
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  return (
    <div>
      <h3 className="text-2xl font-semibold mb-4">Course Reviews</h3>
      {session?.user && (
        <form onSubmit={handleSubmitReview} className="mb-6">
          <div className="mb-4">
            <label className="block mb-2">Your Rating:</label>
            <div className="flex">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setUserRating(star)}
                  className={`text-2xl ${
                    star <= userRating ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>
          <div className="mb-4">
            <label htmlFor="comment" className="block mb-2">
              Your Review:
            </label>
            <textarea
              id="comment"
              value={userComment}
              onChange={(e) => setUserComment(e.target.value)}
              className="w-full px-3 py-2 border rounded"
              rows={4}
            ></textarea>
          </div>
          <Button onClick={() => {}} className="submit-review">Submit Review</Button>
        </form>
      )}
      <div className="space-y-4">
        {reviews.map((review) => (
          <div key={review.id} className="border p-4 rounded">
            <div className="flex items-center mb-2">
              <span className="font-semibold mr-2">{review.userName}</span>
              <span className="text-yellow-400">{'★'.repeat(review.rating)}</span>
              <span className="text-gray-300">{'★'.repeat(5 - review.rating)}</span>
            </div>
            <p>{review.comment}</p>
            <p className="text-sm text-gray-500 mt-2">
              {new Date(review.createdAt).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CourseReviews;
