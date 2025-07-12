#!/usr/bin/env python3
"""
AI 예측 시스템 테스트 스크립트
실시간 예측, 모델 성능, 인사이트 생성 테스트
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIPredictionSystemTester:
    """AI 예측 시스템 테스터"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """관리자 로그인"""
        try:
            login_data = {
                'username': username,
                'password': password
            }
            # 엔드포인트 및 요청 방식 수정
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                logger.info("관리자 로그인 성공")
                return True
            else:
                logger.error(f"로그인 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"로그인 중 오류: {e}")
            return False
    
    def test_real_time_predictions(self) -> Dict[str, Any]:
        """실시간 예측 데이터 테스트"""
        try:
            logger.info("실시간 예측 데이터 테스트 시작")
            
            response = self.session.get(f"{self.base_url}/api/ai/prediction/real-time")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("실시간 예측 데이터 조회 성공")
                
                # 데이터 검증
                predictions = data.get('predictions', {})
                
                # 매출 예측 검증
                if 'sales' in predictions:
                    sales_data = predictions['sales']
                    logger.info(f"매출 예측 데이터: {len(sales_data)}개")
                    for pred in sales_data[:3]:  # 처음 3개만 로그
                        logger.info(f"  - {pred['date']}: {pred['predicted_value']:.0f}원 (신뢰도: {pred['confidence']:.3f})")
                
                # 재고 예측 검증
                if 'inventory' in predictions:
                    inventory_data = predictions['inventory']
                    logger.info(f"재고 예측 데이터: {len(inventory_data)}개")
                    critical_items = [item for item in inventory_data if item['risk_level'] == 'critical']
                    logger.info(f"  - 위험 품목: {len(critical_items)}개")
                
                # 고객 유입 예측 검증
                if 'customer_flow' in predictions:
                    customer_data = predictions['customer_flow']
                    logger.info(f"예상 고객 수: {customer_data.get('total_predicted_customers', 'N/A')}")
                
                # 인력 필요 예측 검증
                if 'staffing' in predictions:
                    staffing_data = predictions['staffing']
                    logger.info(f"필요 인력: {staffing_data.get('needed_staff', 'N/A')}")
                    logger.info(f"현재 인력: {staffing_data.get('current_staff', 'N/A')}")
                
                return {
                    'success': True,
                    'data': data,
                    'message': '실시간 예측 데이터 조회 성공'
                }
            else:
                logger.error(f"실시간 예측 데이터 조회 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': '실시간 예측 데이터 조회 실패'
                }
                
        except Exception as e:
            logger.error(f"실시간 예측 데이터 테스트 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '실시간 예측 데이터 테스트 중 오류 발생'
            }
    
    def test_prediction_accuracy(self) -> Dict[str, Any]:
        """예측 정확도 분석 테스트"""
        try:
            logger.info("예측 정확도 분석 테스트 시작")
            
            response = self.session.get(f"{self.base_url}/api/ai/prediction/accuracy")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("예측 정확도 분석 성공")
                
                # 모델 성능 검증
                model_performance = data.get('model_performance', {})
                logger.info(f"모델 성능 데이터: {len(model_performance)}개 모델")
                
                for model_type, performance in model_performance.items():
                    logger.info(f"  - {model_type}:")
                    logger.info(f"    정확도: {performance['accuracy']:.4f}")
                    logger.info(f"    R²: {performance['r2_score']:.4f}")
                    logger.info(f"    RMSE: {performance['rmse']:.4f}")
                
                # 정확도 트렌드 검증
                accuracy_trends = data.get('accuracy_trends', {})
                if accuracy_trends:
                    logger.info(f"전체 평균 정확도: {accuracy_trends.get('overall_accuracy', 'N/A')}")
                    logger.info(f"총 예측 수: {accuracy_trends.get('total_predictions', 'N/A')}")
                
                return {
                    'success': True,
                    'data': data,
                    'message': '예측 정확도 분석 성공'
                }
            else:
                logger.error(f"예측 정확도 분석 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': '예측 정확도 분석 실패'
                }
                
        except Exception as e:
            logger.error(f"예측 정확도 분석 테스트 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '예측 정확도 분석 테스트 중 오류 발생'
            }
    
    def test_ai_insights(self) -> Dict[str, Any]:
        """AI 인사이트 생성 테스트"""
        try:
            logger.info("AI 인사이트 생성 테스트 시작")
            
            response = self.session.get(f"{self.base_url}/api/ai/prediction/insights")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("AI 인사이트 생성 성공")
                
                # 인사이트 검증
                insights = data.get('insights', [])
                logger.info(f"생성된 인사이트: {len(insights)}개")
                
                for insight in insights:
                    logger.info(f"  - {insight['title']} ({insight['priority']}): {insight['description']}")
                    if insight.get('change_percent'):
                        logger.info(f"    변화율: {insight['change_percent']:.1f}%")
                
                return {
                    'success': True,
                    'data': data,
                    'message': f'AI 인사이트 생성 성공 ({len(insights)}개)'
                }
            else:
                logger.error(f"AI 인사이트 생성 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': 'AI 인사이트 생성 실패'
                }
                
        except Exception as e:
            logger.error(f"AI 인사이트 생성 테스트 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'AI 인사이트 생성 테스트 중 오류 발생'
            }
    
    def test_prediction_alerts(self) -> Dict[str, Any]:
        """예측 기반 알림 테스트"""
        try:
            logger.info("예측 기반 알림 테스트 시작")
            
            response = self.session.get(f"{self.base_url}/api/ai/prediction/alerts")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("예측 기반 알림 조회 성공")
                
                # 알림 검증
                alerts = data.get('alerts', [])
                total_alerts = data.get('total_alerts', 0)
                logger.info(f"발견된 알림: {total_alerts}개")
                
                for alert in alerts:
                    logger.info(f"  - {alert['title']} ({alert['severity']}): {alert['description']}")
                    if alert.get('action_required'):
                        logger.info(f"    조치 필요: 예")
                
                return {
                    'success': True,
                    'data': data,
                    'message': f'예측 기반 알림 조회 성공 ({total_alerts}개)'
                }
            else:
                logger.error(f"예측 기반 알림 조회 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': '예측 기반 알림 조회 실패'
                }
                
        except Exception as e:
            logger.error(f"예측 기반 알림 테스트 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '예측 기반 알림 테스트 중 오류 발생'
            }
    
    def test_model_retrain(self, model_type: str = "sales") -> Dict[str, Any]:
        """모델 재훈련 테스트"""
        try:
            logger.info(f"모델 재훈련 테스트 시작: {model_type}")
            
            response = self.session.post(
                f"{self.base_url}/api/ai/prediction/model/retrain",
                json={'model_type': model_type}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"{model_type} 모델 재훈련 성공")
                
                return {
                    'success': True,
                    'data': data,
                    'message': f'{model_type} 모델 재훈련 성공'
                }
            else:
                logger.error(f"모델 재훈련 실패: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': '모델 재훈련 실패'
                }
                
        except Exception as e:
            logger.error(f"모델 재훈련 테스트 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '모델 재훈련 테스트 중 오류 발생'
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("=== AI 예측 시스템 종합 테스트 시작 ===")
        
        # 로그인
        if not self.login():
            return {
                'success': False,
                'error': '로그인 실패',
                'message': '테스트를 위해 로그인이 필요합니다.'
            }
        
        # 테스트 실행
        tests = [
            ('실시간 예측', self.test_real_time_predictions),
            ('예측 정확도', self.test_prediction_accuracy),
            ('AI 인사이트', self.test_ai_insights),
            ('예측 알림', self.test_prediction_alerts),
            ('모델 재훈련', lambda: self.test_model_retrain("sales"))
        ]
        
        results = {}
        success_count = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} 테스트 ---")
            result = test_func()
            results[test_name] = result
            
            if result['success']:
                success_count += 1
                logger.info(f"✅ {test_name} 테스트 성공")
            else:
                logger.error(f"❌ {test_name} 테스트 실패: {result.get('message', '알 수 없는 오류')}")
        
        # 결과 요약
        total_tests = len(tests)
        success_rate = (success_count / total_tests) * 100
        
        summary = {
            'success': success_count == total_tests,
            'total_tests': total_tests,
            'success_count': success_count,
            'success_rate': success_rate,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\n=== 테스트 결과 요약 ===")
        logger.info(f"총 테스트: {total_tests}개")
        logger.info(f"성공: {success_count}개")
        logger.info(f"실패: {total_tests - success_count}개")
        logger.info(f"성공률: {success_rate:.1f}%")
        
        if success_count == total_tests:
            logger.info("🎉 모든 테스트가 성공했습니다!")
        else:
            logger.warning("⚠️ 일부 테스트가 실패했습니다.")
        
        return summary

    def save_test_results(self, results: Dict[str, Any], filename: str = None):  # pyright: ignore
        """테스트 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_prediction_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 예측 시스템 테스트')
    parser.add_argument('--url', default='http://localhost:5000', help='서버 URL')
    parser.add_argument('--username', default='admin', help='관리자 사용자명')
    parser.add_argument('--password', default='admin123', help='관리자 비밀번호')
    parser.add_argument('--save-results', action='store_true', help='테스트 결과 저장')
    parser.add_argument('--output-file', help='결과 저장 파일명')
    
    args = parser.parse_args()
    
    # 테스터 생성
    tester = AIPredictionSystemTester(args.url)
    
    # 테스트 실행
    results = tester.run_all_tests()
    
    # 결과 저장
    if args.save_results or args.output_file:
        tester.save_test_results(results, args.output_file)
    
    # 종료 코드
    exit_code = 0 if results['success'] else 1
    exit(exit_code)

if __name__ == "__main__":
    main() 