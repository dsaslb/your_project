// 조리 예상시간 안내 알고리즘
// (실제 서비스에서는 DB/통계 기반, 여기선 더미 평균값 사용)

const BASE_AVG_TIME = 10; // 기본 평균 조리시간(분)

export default function estimateCookingTime(orderCount: number, feedbackAvg?: number) {
  // 피드백 기반 평균 조리시간 반영
  const avg = feedbackAvg || BASE_AVG_TIME;
  // 주문 수에 따라 가중치 적용(예: 3개 이상이면 1.5배)
  let factor = 1;
  if (orderCount >= 5) factor = 2;
  else if (orderCount >= 3) factor = 1.5;
  return Math.round(avg * factor);
}
