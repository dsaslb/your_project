import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Feedback {
  id: number;
  review: string;
  nps_score: number;
  sentiment?: string;
}

interface Props {
  storeId: number;
}

export default function FeedbackDashboard({ storeId }: Props) {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  useEffect(() => {
    axios.get(`/api/feedback/list?store_id=${storeId}`).then(res => setFeedbacks(res.data));
  }, [storeId]);
  return (
    <div>
      <h2>고객 피드백</h2>
      <ul>
        {feedbacks.map(f => (
          <li key={f.id}>
            {f.review} (NPS: {f.nps_score}) <span>{f.sentiment}</span>
          </li>
        ))}
      </ul>
    </div>
  );
} 