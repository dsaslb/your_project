"""
AI Client for Main Flask App
메인 Flask 앱에서 AI 예측 서버와 통신하는 클라이언트
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, base_url: str = "http://localhost:8501", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """AI 서버 상태 확인"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"AI server health check failed: {e}")
            return False
    
    def predict_sales(self, days: int = 7, base_sales: float = 1000) -> Optional[Dict[str, Any]]:
        """매출 예측"""
        try:
            data = {
                "data": {
                    "days": days,
                    "base_sales": base_sales
                },
                "model_type": "sales_forecast"
            }
            
            response = self.session.post(
                f"{self.base_url}/predict",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Sales prediction failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Sales prediction error: {e}")
            return None
    
    def predict_demand(self, items: List[str], base_demand: int = 50) -> Optional[Dict[str, Any]]:
        """수요 예측"""
        try:
            data = {
                "data": {
                    "items": items,
                    "base_demand": base_demand
                },
                "model_type": "demand_prediction"
            }
            
            response = self.session.post(
                f"{self.base_url}/predict",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # 결과를 아이템별 딕셔너리로 변환
                predictions = {}
                confidences = {}
                for i, item in enumerate(items):
                    if i < len(result.get('prediction', [])):
                        predictions[item] = result['prediction'][i]
                        confidences[item] = result['confidence'][i]
                
                return {
                    "prediction": predictions,
                    "confidence": confidences,
                    "model_info": result.get('model_info', {})
                }
            else:
                logger.error(f"Demand prediction failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Demand prediction error: {e}")
            return None
    
    def get_available_models(self) -> Optional[Dict[str, Any]]:
        """사용 가능한 모델 목록 조회"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get models: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Get models error: {e}")
            return None

# 전역 AI 클라이언트 인스턴스
ai_client = AIClient()

def get_ai_client() -> AIClient:
    """AI 클라이언트 인스턴스 반환"""
    return ai_client

# 편의 함수들
def predict_weekly_sales(base_sales: float = 1000) -> Optional[Dict[str, Any]]:
    """주간 매출 예측"""
    return ai_client.predict_sales(days=7, base_sales=base_sales)

def predict_monthly_sales(base_sales: float = 1000) -> Optional[Dict[str, Any]]:
    """월간 매출 예측"""
    return ai_client.predict_sales(days=30, base_sales=base_sales)

def predict_menu_demand(menu_items: List[str]) -> Optional[Dict[str, Any]]:
    """메뉴별 수요 예측"""
    return ai_client.predict_demand(items=menu_items)

def is_ai_server_available() -> bool:
    """AI 서버 사용 가능 여부 확인"""
    return ai_client.health_check() 