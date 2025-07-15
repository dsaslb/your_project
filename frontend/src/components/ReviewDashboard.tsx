import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Review {
  content: string;
  rating: number;
}

interface Props {
  brandId: number;
}

export default function ReviewDashboard({ brandId }: Props) {
  const [reviews, setReviews] = useState<Review[]>([]);
  useEffect(() => {
    axios.get(`/api/external/reviews?brand_id=${brandId}`).then(res => setReviews(res.data.reviews || []));
  }, [brandId]);
  return (
    <div>
      <h2>실시간 리뷰</h2>
      <ul>
        {reviews.map((r, i) => <li key={i}>{r.content} ({r.rating}점)</li>)}
      </ul>
    </div>
  );
} 