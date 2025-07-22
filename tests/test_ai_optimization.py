"""
AI 기반 성능 예측/이상 탐지/자동화 테스트
"""
import unittest
from ai.ai_performance_optimizer import get_ai_optimizer
from datetime import datetime, timedelta
import random

class TestAIPerformanceOptimizer(unittest.TestCase):
    def setUp(self):
        self.ai = get_ai_optimizer()
        # 테스트용 메트릭 데이터 생성
        now = datetime.now()
        self.metrics = [
            {
                'timestamp': (now - timedelta(minutes=i)).timestamp(),
                'cpu_usage': random.uniform(10, 90),
                'memory_usage': random.uniform(20, 80),
                'response_time_avg': random.uniform(0.1, 2.5),
                'error_count': random.randint(0, 5)
            }
            for i in range(60)
        ]

    def test_anomaly_detection(self):
        # 이상 탐지 모델 학습 및 이상 탐지
        self.ai.fit_anomaly_model(self.metrics)
        anomalies = self.ai.detect_anomalies(self.metrics)
        self.assertIsInstance(anomalies, list)
        # 이상치가 0개 이상이어야 함
        self.assertGreaterEqual(len(anomalies), 0)

    def test_forecast(self):
        # 미래 CPU/메모리 예측
        self.ai.fit_forecast_model(self.metrics, 'cpu_usage')
        cpu_pred = self.ai.predict_future(self.metrics, 'cpu_usage', steps=5)
        self.assertIsInstance(cpu_pred, list)
        self.assertEqual(len(cpu_pred), 5)

    def test_auto_optimize_signal(self):
        # 자동화 신호 생성
        signal = self.ai.auto_optimize_signal(self.metrics)
        self.assertIn('anomaly_detected', signal)
        self.assertIn('future_cpu', signal)
        self.assertIn('scale_up', signal)
        self.assertIn('scale_down', signal)

if __name__ == '__main__':
    unittest.main() 