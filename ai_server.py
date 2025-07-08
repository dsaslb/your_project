"""
AI Prediction Server (FastAPI)
메인 Flask 앱에서 AI 예측 기능을 호출할 수 있는 REST API 서버
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant AI Prediction Server", version="1.0.0")

# Pydantic 모델들
class PredictionRequest(BaseModel):
    data: Dict[str, Any]
    model_type: str = "sales_forecast"  # sales_forecast, demand_prediction, etc.

class PredictionResponse(BaseModel):
    prediction: List[float]
    confidence: List[float]
    model_info: Dict[str, Any]

# 더미 AI 모델 (실제로는 TensorFlow 모델 로드)
class DummyAIModel:
    def __init__(self):
        self.model_type = "dummy"
        logger.info("Dummy AI Model initialized")
    
    def predict_sales(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """매출 예측 (더미 구현)"""
        # 실제로는 TensorFlow 모델로 예측
        days = data.get('days', 7)
        base_sales = data.get('base_sales', 1000)
        
        # 간단한 시계열 예측 시뮬레이션
        predictions = []
        confidences = []
        
        for i in range(days):
            # 주말 효과, 계절성 등 고려
            weekend_factor = 1.2 if (i % 7) >= 5 else 1.0
            trend_factor = 1 + (i * 0.02)  # 상승 트렌드
            noise = np.random.normal(0, 0.1)
            
            pred = base_sales * weekend_factor * trend_factor * (1 + noise)
            predictions.append(max(0, pred))
            confidences.append(0.85 + np.random.normal(0, 0.05))
        
        return {
            "prediction": predictions,
            "confidence": confidences,
            "model_info": {
                "model_type": "sales_forecast",
                "version": "1.0.0",
                "features_used": list(data.keys())
            }
        }
    
    def predict_demand(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """수요 예측 (더미 구현)"""
        items = data.get('items', ['burger', 'pizza', 'salad'])
        base_demand = data.get('base_demand', 50)
        
        predictions = []
        confidences = []
        
        for item in items:
            # 각 아이템별 수요 예측
            item_pred = base_demand * np.random.uniform(0.8, 1.2)
            predictions.append(max(0, int(item_pred)))
            confidences.append(0.8 + np.random.normal(0, 0.1))
        
        return {
            "prediction": predictions,
            "confidence": confidences,
            "model_info": {
                "model_type": "demand_prediction",
                "version": "1.0.0",
                "items_analyzed": items
            }
        }

# AI 모델 인스턴스
ai_model = DummyAIModel()

@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "status": "running",
        "service": "Restaurant AI Prediction Server",
        "version": "1.0.0",
        "available_models": ["sales_forecast", "demand_prediction"]
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """AI 예측 API"""
    try:
        logger.info(f"Prediction request received: {request.model_type}")
        
        if request.model_type == "sales_forecast":
            result = ai_model.predict_sales(request.data)
        elif request.model_type == "demand_prediction":
            result = ai_model.predict_demand(request.data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model type: {request.model_type}")
        
        return PredictionResponse(**result)
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/models")
async def list_models():
    """사용 가능한 모델 목록"""
    return {
        "available_models": [
            {
                "name": "sales_forecast",
                "description": "매출 예측 모델",
                "input_format": {
                    "days": "int (예측 기간)",
                    "base_sales": "float (기준 매출)"
                }
            },
            {
                "name": "demand_prediction", 
                "description": "수요 예측 모델",
                "input_format": {
                    "items": "list (아이템 목록)",
                    "base_demand": "int (기준 수요)"
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501) 