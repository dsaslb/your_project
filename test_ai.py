#!/usr/bin/env python3
"""
AI 서버 및 클라이언트 테스트 스크립트
"""

from ai_client import is_ai_server_available, predict_weekly_sales, predict_menu_demand

def test_ai_server():
    print("=== AI 서버 테스트 ===")
    
    # 서버 상태 확인
    print("1. AI 서버 상태 확인...")
    available = is_ai_server_available()
    print(f"   AI Server Available: {available}")
    
    if not available:
        print("   ❌ AI 서버에 연결할 수 없습니다.")
        return
    
    print("   ✅ AI 서버가 정상적으로 실행 중입니다.")
    
    # 매출 예측 테스트
    print("\n2. 매출 예측 테스트...")
    sales_result = predict_weekly_sales(1000)
    if sales_result:
        print("   ✅ 매출 예측 성공")
        print(f"   예측 결과: {sales_result['prediction'][:3]}... (처음 3일)")
        print(f"   신뢰도: {sales_result['confidence'][:3]}... (처음 3일)")
    else:
        print("   ❌ 매출 예측 실패")
    
    # 수요 예측 테스트
    print("\n3. 수요 예측 테스트...")
    menu_items = ['버거', '피자', '샐러드', '음료']
    demand_result = predict_menu_demand(menu_items)
    if demand_result:
        print("   ✅ 수요 예측 성공")
        print(f"   예측 결과: {demand_result['prediction']}")
    else:
        print("   ❌ 수요 예측 실패")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_ai_server() 