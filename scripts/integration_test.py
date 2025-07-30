# -*- coding: utf-8 -*-
"""
전체 시스템 통합 테스트
AI 기반 시스템의 모든 기능을 종합적으로 테스트
"""

import time
import json
from datetime import datetime

def test_system_health():
    """시스템 상태 테스트"""
    print("🔍 시스템 상태 테스트...")
    try:
        from utils.system_health_checker import run_quick_health_check
        result = run_quick_health_check()
        print(f"✅ 시스템 상태: {result['status']}")
        print(f"   메시지: {result['message']}")
        return result['status'] == 'healthy'
    except Exception as e:
        print(f"❌ 시스템 상태 테스트 실패: {e}")
        return False

def test_ai_prediction():
    """AI 예측 테스트"""
    print("\n🧠 AI 예측 테스트...")
    try:
        from ai.performance_predictor import predict_future_performance
        predictions = predict_future_performance(6)  # 6시간 예측
        
        if predictions:
            print("✅ AI 예측 성공")
            print(f"   CPU 예측: {len(predictions.get('cpu_percent', []))}개 데이터")
            print(f"   메모리 예측: {len(predictions.get('memory_percent', []))}개 데이터")
            print(f"   응답시간 예측: {len(predictions.get('response_time', []))}개 데이터")
            return True
        else:
            print("❌ AI 예측 실패: 예측 데이터 없음")
            return False
    except Exception as e:
        print(f"❌ AI 예측 테스트 실패: {e}")
        return False

def test_performance_analysis():
    """성능 분석 테스트"""
    print("\n📊 성능 분석 테스트...")
    try:
        from ai.performance_predictor import get_performance_analysis
        analysis = get_performance_analysis()
        
        if analysis and 'trends' in analysis:
            print("✅ 성능 분석 성공")
            print(f"   시간대별 평균: {len(analysis['trends'].get('hourly_averages', {}))}개 시간대")
            print(f"   요일별 평균: {len(analysis['trends'].get('daily_averages', {}))}개 요일")
            print(f"   패턴 분석: {len(analysis['trends'].get('patterns', {}))}개 패턴")
            return True
        else:
            print("❌ 성능 분석 실패: 분석 데이터 없음")
            return False
    except Exception as e:
        print(f"❌ 성능 분석 테스트 실패: {e}")
        return False

def test_mobile_notifications():
    """모바일 알림 테스트"""
    print("\n📱 모바일 알림 테스트...")
    try:
        from utils.mobile_notification_system import send_system_alert, send_performance_alert
        
        # 시스템 알림 테스트
        result1 = send_system_alert(
            "통합 테스트 알림",
            "시스템 통합 테스트가 진행 중입니다.",
            "warning",
            "integration_test"
        )
        
        # 성능 알림 테스트
        result2 = send_performance_alert("테스트 메트릭", 75.0, 70.0, "warning")
        
        if result1 and result2:
            print("✅ 모바일 알림 테스트 성공")
            print("   시스템 알림: 발송됨")
            print("   성능 알림: 발송됨")
            return True
        else:
            print("❌ 모바일 알림 테스트 실패")
            return False
    except Exception as e:
        print(f"❌ 모바일 알림 테스트 실패: {e}")
        return False

def test_performance_monitoring():
    """성능 모니터링 테스트"""
    print("\n📈 성능 모니터링 테스트...")
    try:
        from scripts.performance_monitor import get_performance_status
        status = get_performance_status()
        
        if status and 'current_status' in status:
            print("✅ 성능 모니터링 테스트 성공")
            print(f"   상태: {status.get('current_status', 'unknown')}")
            print(f"   데이터 포인트: {status.get('data_points', 0)}개")
            return True
        else:
            print("❌ 성능 모니터링 테스트 실패: 상태 정보 없음")
            return False
    except Exception as e:
        print(f"❌ 성능 모니터링 테스트 실패: {e}")
        return False

def test_automated_maintenance():
    """자동 유지보수 테스트"""
    print("\n🔧 자동 유지보수 테스트...")
    try:
        from scripts.automated_maintenance import run_manual_maintenance
        result = run_manual_maintenance()
        
        if result and result.get('status') == 'success':
            print("✅ 자동 유지보수 테스트 성공")
            print(f"   메시지: {result.get('message', 'N/A')}")
            return True
        else:
            print("❌ 자동 유지보수 테스트 실패")
            return False
    except Exception as e:
        print(f"❌ 자동 유지보수 테스트 실패: {e}")
        return False

def test_data_integrity():
    """데이터 무결성 테스트"""
    print("\n💾 데이터 무결성 테스트...")
    try:
        import sqlite3
        
        # 성능 데이터 확인
        conn = sqlite3.connect('data/performance_metrics.db')
        cursor = conn.cursor()
        
        # 데이터 개수 확인
        cursor.execute('SELECT COUNT(*) FROM performance_metrics')
        data_count = cursor.fetchone()[0]
        
        # 최근 데이터 확인
        cursor.execute('SELECT MAX(timestamp) FROM performance_metrics')
        latest_timestamp = cursor.fetchone()[0]
        
        conn.close()
        
        if data_count > 0 and latest_timestamp:
            print("✅ 데이터 무결성 테스트 성공")
            print(f"   총 데이터: {data_count}개")
            print(f"   최근 데이터: {latest_timestamp}")
            return True
        else:
            print("❌ 데이터 무결성 테스트 실패: 데이터 없음")
            return False
    except Exception as e:
        print(f"❌ 데이터 무결성 테스트 실패: {e}")
        return False

def run_integration_test():
    """통합 테스트 실행"""
    print("🚀 AI 기반 시스템 통합 테스트 시작")
    print("=" * 50)
    
    start_time = time.time()
    test_results = {}
    
    # 각 테스트 실행
    test_results['system_health'] = test_system_health()
    test_results['ai_prediction'] = test_ai_prediction()
    test_results['performance_analysis'] = test_performance_analysis()
    test_results['mobile_notifications'] = test_mobile_notifications()
    test_results['performance_monitoring'] = test_performance_monitoring()
    test_results['automated_maintenance'] = test_automated_maintenance()
    test_results['data_integrity'] = test_data_integrity()
    
    # 결과 요약
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📋 통합 테스트 결과 요약")
    print("=" * 50)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n총 테스트: {total_tests}개")
    print(f"통과: {passed_tests}개")
    print(f"실패: {total_tests - passed_tests}개")
    print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
    print(f"소요시간: {duration:.2f}초")
    
    # 전체 결과
    if passed_tests == total_tests:
        print("\n🎉 모든 테스트가 성공적으로 통과했습니다!")
        print("AI 기반 시스템이 정상적으로 작동하고 있습니다.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests}개의 테스트가 실패했습니다.")
        print("일부 기능에 문제가 있을 수 있습니다.")
    
    return test_results

if __name__ == "__main__":
    run_integration_test() 