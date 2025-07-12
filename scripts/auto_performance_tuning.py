#!/usr/bin/env python3
"""
자동 성능 튜닝 시스템
운영 데이터 분석을 기반으로 시스템 성능을 자동으로 최적화
"""

import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TuningAction:
    """튜닝 액션 데이터 클래스"""
    action_type: str
    target: str
    parameter: str
    old_value: Any
    new_value: Any
    reason: str
    priority: str
    estimated_impact: str

class AutoPerformanceTuner:
    """자동 성능 튜닝 시스템"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tuning_history = []
        self.tuning_config = {
            'enable_auto_tuning': True,
            'tuning_interval': 3600,  # 1시간
            'min_health_score': 70.0,  # 최소 건강도 점수
            'max_tuning_actions': 5,   # 최대 튜닝 액션 수
            'tuning_thresholds': {
                'response_time': {
                    'warning': 2.0,
                    'critical': 5.0,
                    'tuning_factor': 0.8  # 20% 개선 목표
                },
                'memory_usage': {
                    'warning': 80.0,
                    'critical': 95.0,
                    'tuning_factor': 0.9  # 10% 개선 목표
                },
                'cpu_usage': {
                    'warning': 85.0,
                    'critical': 95.0,
                    'tuning_factor': 0.9  # 10% 개선 목표
                },
                'error_rate': {
                    'warning': 5.0,
                    'critical': 15.0,
                    'tuning_factor': 0.5  # 50% 개선 목표
                }
            }
        }
        
    def start_auto_tuning(self) -> Dict[str, Any]:
        """자동 튜닝 시작"""
        logger.info("자동 성능 튜닝 시스템 시작")
        
        try:
            # 성능 분석 시스템 시작
            response = self.session.post(f"{self.base_url}/api/performance/start")
            if not response.json().get('success'):
                return {
                    'status': 'error',
                    'message': '성능 분석 시스템 시작 실패'
                }
            
            # 초기 튜닝 수행
            initial_tuning = self.perform_tuning_cycle()
            
            return {
                'status': 'success',
                'message': '자동 튜닝 시스템이 시작되었습니다',
                'initial_tuning': initial_tuning
            }
            
        except Exception as e:
            logger.error(f"자동 튜닝 시작 실패: {e}")
            return {
                'status': 'error',
                'message': f'자동 튜닝 시작 실패: {e}'
            }
    
    def stop_auto_tuning(self) -> Dict[str, Any]:
        """자동 튜닝 중지"""
        logger.info("자동 성능 튜닝 시스템 중지")
        
        try:
            # 성능 분석 시스템 중지
            response = self.session.post(f"{self.base_url}/api/performance/stop")
            if not response.json().get('success'):
                return {
                    'status': 'error',
                    'message': '성능 분석 시스템 중지 실패'
                }
            
            return {
                'status': 'success',
                'message': '자동 튜닝 시스템이 중지되었습니다',
                'tuning_history': self.tuning_history
            }
            
        except Exception as e:
            logger.error(f"자동 튜닝 중지 실패: {e}")
            return {
                'status': 'error',
                'message': f'자동 튜닝 중지 실패: {e}'
            }
    
    def perform_tuning_cycle(self) -> Dict[str, Any]:
        """튜닝 사이클 수행"""
        logger.info("튜닝 사이클 시작")
        
        try:
            # 현재 성능 상태 분석
            performance_data = self.get_current_performance()
            if not performance_data:
                return {
                    'status': 'error',
                    'message': '성능 데이터를 가져올 수 없습니다'
                }
            
            # 튜닝 필요성 판단
            if not self.needs_tuning(performance_data):
                return {
                    'status': 'no_action',
                    'message': '튜닝이 필요하지 않습니다',
                    'health_score': performance_data.get('health_score', 0)
                }
            
            # 튜닝 액션 생성
            tuning_actions = self.generate_tuning_actions(performance_data)
            if not tuning_actions:
                return {
                    'status': 'no_action',
                    'message': '적용 가능한 튜닝 액션이 없습니다'
                }
            
            # 튜닝 액션 적용
            applied_actions = self.apply_tuning_actions(tuning_actions)
            
            # 튜닝 결과 검증
            verification_result = self.verify_tuning_results(applied_actions)
            
            return {
                'status': 'success',
                'message': f'{len(applied_actions)}개의 튜닝 액션이 적용되었습니다',
                'applied_actions': applied_actions,
                'verification': verification_result,
                'before_health_score': performance_data.get('health_score', 0),
                'after_health_score': verification_result.get('health_score', 0)
            }
            
        except Exception as e:
            logger.error(f"튜닝 사이클 실패: {e}")
            return {
                'status': 'error',
                'message': f'튜닝 사이클 실패: {e}'
            }
    
    def get_current_performance(self) -> Optional[Dict[str, Any]]:
        """현재 성능 상태 조회"""
        try:
            # 성능 리포트 조회
            response = self.session.get(f"{self.base_url}/api/performance/report")
            data = response.json()
            
            if not data.get('success'):
                logger.error(f"성능 리포트 조회 실패: {data.get('error')}")
                return None
            
            return data.get('data', {})
            
        except Exception as e:
            logger.error(f"성능 상태 조회 실패: {e}")
            return None
    
    def needs_tuning(self, performance_data: Dict[str, Any]) -> bool:
        """튜닝 필요성 판단"""
        health_score = performance_data.get('health_score', 100)
        
        # 건강도 점수가 임계값보다 낮으면 튜닝 필요
        if health_score < self.tuning_config['min_health_score']:
            logger.info(f"건강도 점수가 낮아 튜닝이 필요합니다: {health_score}")
            return True
        
        # 병목 지점이 있으면 튜닝 필요
        bottlenecks = performance_data.get('bottlenecks', [])
        if bottlenecks:
            logger.info(f"병목 지점이 발견되어 튜닝이 필요합니다: {len(bottlenecks)}개")
            return True
        
        logger.info("튜닝이 필요하지 않습니다")
        return False
    
    def generate_tuning_actions(self, performance_data: Dict[str, Any]) -> List[TuningAction]:
        """튜닝 액션 생성"""
        actions = []
        
        # 병목 지점 기반 튜닝 액션
        bottlenecks = performance_data.get('bottlenecks', [])
        for bottleneck in bottlenecks:
            bottleneck_actions = self.generate_bottleneck_actions(bottleneck)
            actions.extend(bottleneck_actions)
        
        # 메트릭 기반 튜닝 액션
        metrics_summary = performance_data.get('metrics_summary', {})
        metric_actions = self.generate_metric_actions(metrics_summary)
        actions.extend(metric_actions)
        
        # 우선순위별 정렬 및 제한
        actions.sort(key=lambda x: self.get_action_priority(x.priority), reverse=True)
        actions = actions[:self.tuning_config['max_tuning_actions']]
        
        logger.info(f"{len(actions)}개의 튜닝 액션이 생성되었습니다")
        return actions
    
    def generate_bottleneck_actions(self, bottleneck: Dict[str, Any]) -> List[TuningAction]:
        """병목 지점 기반 튜닝 액션 생성"""
        actions = []
        bottleneck_type = bottleneck.get('type', '')
        severity = bottleneck.get('severity', 'warning')
        
        if bottleneck_type == 'response_time':
            actions.append(TuningAction(
                action_type='cache_optimization',
                target='api_cache',
                parameter='cache_ttl',
                old_value=300,
                new_value=600,
                reason='응답 시간 개선을 위한 캐시 TTL 증가',
                priority=severity,
                estimated_impact='response_time_improvement'
            ))
            
            actions.append(TuningAction(
                action_type='database_optimization',
                target='query_cache',
                parameter='enable_query_cache',
                old_value=False,
                new_value=True,
                reason='데이터베이스 쿼리 캐싱 활성화',
                priority=severity,
                estimated_impact='response_time_improvement'
            ))
        
        elif bottleneck_type == 'memory_usage':
            actions.append(TuningAction(
                action_type='memory_optimization',
                target='garbage_collection',
                parameter='gc_frequency',
                old_value='normal',
                new_value='aggressive',
                reason='메모리 사용량 감소를 위한 가비지 컬렉션 강화',
                priority=severity,
                estimated_impact='memory_usage_reduction'
            ))
            
            actions.append(TuningAction(
                action_type='cache_optimization',
                target='memory_cache',
                parameter='max_cache_size',
                old_value='unlimited',
                new_value='512MB',
                reason='메모리 캐시 크기 제한',
                priority=severity,
                estimated_impact='memory_usage_reduction'
            ))
        
        elif bottleneck_type == 'cpu_usage':
            actions.append(TuningAction(
                action_type='thread_optimization',
                target='worker_threads',
                parameter='max_workers',
                old_value=10,
                new_value=5,
                reason='CPU 사용량 감소를 위한 워커 스레드 수 조정',
                priority=severity,
                estimated_impact='cpu_usage_reduction'
            ))
            
            actions.append(TuningAction(
                action_type='scheduling_optimization',
                target='task_scheduler',
                parameter='task_priority',
                old_value='normal',
                new_value='low',
                reason='비중요 작업 우선순위 낮춤',
                priority=severity,
                estimated_impact='cpu_usage_reduction'
            ))
        
        elif bottleneck_type == 'error_rate':
            actions.append(TuningAction(
                action_type='error_handling',
                target='circuit_breaker',
                parameter='enable_circuit_breaker',
                old_value=False,
                new_value=True,
                reason='에러율 감소를 위한 서킷 브레이커 활성화',
                priority=severity,
                estimated_impact='error_rate_reduction'
            ))
            
            actions.append(TuningAction(
                action_type='retry_optimization',
                target='retry_policy',
                parameter='max_retries',
                old_value=3,
                new_value=1,
                reason='재시도 횟수 감소로 에러 전파 방지',
                priority=severity,
                estimated_impact='error_rate_reduction'
            ))
        
        return actions
    
    def generate_metric_actions(self, metrics_summary: Dict[str, Any]) -> List[TuningAction]:
        """메트릭 기반 튜닝 액션 생성"""
        actions = []
        
        # 응답 시간 최적화
        avg_response_time = metrics_summary.get('avg_response_time', 0)
        if avg_response_time > self.tuning_config['tuning_thresholds']['response_time']['warning']:
            actions.append(TuningAction(
                action_type='compression_optimization',
                target='response_compression',
                parameter='enable_gzip',
                old_value=False,
                new_value=True,
                reason='응답 압축 활성화로 전송 시간 단축',
                priority='medium',
                estimated_impact='response_time_improvement'
            ))
        
        # 메모리 사용량 최적화
        avg_memory_usage = metrics_summary.get('avg_memory_usage', 0)
        if avg_memory_usage > self.tuning_config['tuning_thresholds']['memory_usage']['warning']:
            actions.append(TuningAction(
                action_type='memory_cleanup',
                target='memory_cleanup',
                parameter='cleanup_interval',
                old_value=3600,
                new_value=1800,
                reason='메모리 정리 주기 단축',
                priority='medium',
                estimated_impact='memory_usage_reduction'
            ))
        
        return actions
    
    def get_action_priority(self, priority: str) -> int:
        """액션 우선순위 점수 반환"""
        priority_scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_scores.get(priority, 0)
    
    def apply_tuning_actions(self, actions: List[TuningAction]) -> List[Dict[str, Any]]:
        """튜닝 액션 적용"""
        applied_actions = []
        
        for action in actions:
            try:
                # 실제 시스템에 튜닝 적용 (시뮬레이션)
                success = self.apply_single_action(action)
                
                applied_action = {
                    'action': action,
                    'success': success,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'{action.action_type} 적용 {"성공" if success else "실패"}'
                }
                
                applied_actions.append(applied_action)
                
                if success:
                    self.tuning_history.append(applied_action)
                    logger.info(f"튜닝 액션 적용 성공: {action.action_type}")
                else:
                    logger.warning(f"튜닝 액션 적용 실패: {action.action_type}")
                
                # 액션 간 간격
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"튜닝 액션 적용 중 오류: {e}")
                applied_actions.append({
                    'action': action,
                    'success': False,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'오류 발생: {e}'
                })
        
        return applied_actions
    
    def apply_single_action(self, action: TuningAction) -> bool:
        """단일 튜닝 액션 적용 (시뮬레이션)"""
        try:
            # 실제 구현에서는 각 액션 타입에 맞는 시스템 설정 변경
            if action.action_type == 'cache_optimization':
                # 캐시 설정 변경 API 호출
                return self.update_cache_settings(action)
            elif action.action_type == 'database_optimization':
                # 데이터베이스 설정 변경 API 호출
                return self.update_database_settings(action)
            elif action.action_type == 'memory_optimization':
                # 메모리 설정 변경 API 호출
                return self.update_memory_settings(action)
            elif action.action_type == 'thread_optimization':
                # 스레드 설정 변경 API 호출
                return self.update_thread_settings(action)
            elif action.action_type == 'error_handling':
                # 에러 처리 설정 변경 API 호출
                return self.update_error_handling_settings(action)
            else:
                # 기본적으로 성공으로 처리 (시뮬레이션)
                return True
                
        except Exception as e:
            logger.error(f"액션 적용 실패: {e}")
            return False
    
    def update_cache_settings(self, action: TuningAction) -> bool:
        """캐시 설정 업데이트 (시뮬레이션)"""
        # 실제 구현에서는 캐시 설정 API 호출
        logger.info(f"캐시 설정 업데이트: {action.target} = {action.new_value}")
        return True
    
    def update_database_settings(self, action: TuningAction) -> bool:
        """데이터베이스 설정 업데이트 (시뮬레이션)"""
        # 실제 구현에서는 데이터베이스 설정 API 호출
        logger.info(f"데이터베이스 설정 업데이트: {action.target} = {action.new_value}")
        return True
    
    def update_memory_settings(self, action: TuningAction) -> bool:
        """메모리 설정 업데이트 (시뮬레이션)"""
        # 실제 구현에서는 메모리 설정 API 호출
        logger.info(f"메모리 설정 업데이트: {action.target} = {action.new_value}")
        return True
    
    def update_thread_settings(self, action: TuningAction) -> bool:
        """스레드 설정 업데이트 (시뮬레이션)"""
        # 실제 구현에서는 스레드 설정 API 호출
        logger.info(f"스레드 설정 업데이트: {action.target} = {action.new_value}")
        return True
    
    def update_error_handling_settings(self, action: TuningAction) -> bool:
        """에러 처리 설정 업데이트 (시뮬레이션)"""
        # 실제 구현에서는 에러 처리 설정 API 호출
        logger.info(f"에러 처리 설정 업데이트: {action.target} = {action.new_value}")
        return True
    
    def verify_tuning_results(self, applied_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """튜닝 결과 검증"""
        try:
            # 튜닝 후 성능 상태 확인
            time.sleep(5)  # 튜닝 효과가 반영될 시간 대기
            
            performance_data = self.get_current_performance()
            if not performance_data:
                return {
                    'status': 'error',
                    'message': '튜닝 후 성능 데이터를 가져올 수 없습니다'
                }
            
            # 튜닝 효과 분석
            health_score = performance_data.get('health_score', 0)
            bottlenecks = performance_data.get('bottlenecks', [])
            
            return {
                'status': 'success',
                'health_score': health_score,
                'bottlenecks_count': len(bottlenecks),
                'improvement': health_score > 70,  # 임시 기준
                'message': f'튜닝 후 건강도 점수: {health_score:.1f}'
            }
            
        except Exception as e:
            logger.error(f"튜닝 결과 검증 실패: {e}")
            return {
                'status': 'error',
                'message': f'튜닝 결과 검증 실패: {e}'
            }
    
    def get_tuning_report(self) -> Dict[str, Any]:
        """튜닝 리포트 생성"""
        return {
            'timestamp': datetime.now().isoformat(),
            'tuning_history': self.tuning_history,
            'total_actions': len(self.tuning_history),
            'successful_actions': len([a for a in self.tuning_history if a['success']]),
            'failed_actions': len([a for a in self.tuning_history if not a['success']]),
            'config': self.tuning_config
        }

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='자동 성능 튜닝 시스템')
    parser.add_argument('--url', default='http://localhost:5000', help='서버 URL')
    parser.add_argument('--action', choices=['start', 'stop', 'tune', 'report'], 
                       default='tune', help='수행할 액션')
    parser.add_argument('--output', default='tuning_report.json', help='결과 파일 경로')
    
    args = parser.parse_args()
    
    # 튜너 생성
    tuner = AutoPerformanceTuner(args.url)
    
    if args.action == 'start':
        result = tuner.start_auto_tuning()
    elif args.action == 'stop':
        result = tuner.stop_auto_tuning()
    elif args.action == 'tune':
        result = tuner.perform_tuning_cycle()
    elif args.action == 'report':
        result = tuner.get_tuning_report()
    
    # 결과 출력
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 결과 파일 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n결과가 '{args.output}'에 저장되었습니다")

if __name__ == "__main__":
    main() 