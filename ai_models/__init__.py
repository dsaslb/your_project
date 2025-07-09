"""
AI 모델 패키지
실제 TensorFlow/PyTorch 기반 AI 분석 모델들을 포함합니다.
"""

# 기본 모델은 항상 import
from .sales_prediction import SalesPredictionModel

# 조건부 import - 파일이 존재하는 경우에만 import
try:
    from .staff_optimization import StaffOptimizationModel
    STAFF_OPTIMIZATION_AVAILABLE = True
except ImportError:
    StaffOptimizationModel = None
    STAFF_OPTIMIZATION_AVAILABLE = False

try:
    from .inventory_forecasting import InventoryForecastingModel
    INVENTORY_FORECASTING_AVAILABLE = True
except ImportError:
    InventoryForecastingModel = None
    INVENTORY_FORECASTING_AVAILABLE = False

try:
    from .customer_analytics import CustomerAnalyticsModel
    CUSTOMER_ANALYTICS_AVAILABLE = True
except ImportError:
    CustomerAnalyticsModel = None
    CUSTOMER_ANALYTICS_AVAILABLE = False

# 사용 가능한 모델들만 __all__에 포함
__all__ = ['SalesPredictionModel']

if STAFF_OPTIMIZATION_AVAILABLE:
    __all__.append('StaffOptimizationModel')

if INVENTORY_FORECASTING_AVAILABLE:
    __all__.append('InventoryForecastingModel')

if CUSTOMER_ANALYTICS_AVAILABLE:
    __all__.append('CustomerAnalyticsModel')

# 사용 가능한 모델 정보
AVAILABLE_MODELS = {
    'sales_prediction': True,
    'staff_optimization': STAFF_OPTIMIZATION_AVAILABLE,
    'inventory_forecasting': INVENTORY_FORECASTING_AVAILABLE,
    'customer_analytics': CUSTOMER_ANALYTICS_AVAILABLE
}

def get_available_models():
    """사용 가능한 AI 모델 목록 반환"""
    return {k: v for k, v in AVAILABLE_MODELS.items() if v}

def create_model(model_type: str, **kwargs):
    """모델 타입에 따라 AI 모델 인스턴스 생성"""
    if model_type == 'sales_prediction':
        return SalesPredictionModel(**kwargs)
    elif model_type == 'staff_optimization' and STAFF_OPTIMIZATION_AVAILABLE and StaffOptimizationModel is not None:
        return StaffOptimizationModel(**kwargs)
    elif model_type == 'inventory_forecasting' and INVENTORY_FORECASTING_AVAILABLE and InventoryForecastingModel is not None:
        return InventoryForecastingModel(**kwargs)
    elif model_type == 'customer_analytics' and CUSTOMER_ANALYTICS_AVAILABLE and CustomerAnalyticsModel is not None:
        return CustomerAnalyticsModel(**kwargs)
    else:
        available_models = get_available_models()
        raise ValueError(f"지원하지 않는 모델 타입: {model_type}. 사용 가능한 모델: {list(available_models.keys())}") 