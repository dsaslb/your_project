#!/usr/bin/env python3
"""
AI 환경 설정 스크립트
TensorFlow 설치 확인 및 초기화
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        return False
    print(f"✅ Python 버전 확인: {sys.version}")
    return True

def install_tensorflow():
    """TensorFlow 설치"""
    try:
        print("🔧 TensorFlow 설치 중...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "tensorflow>=2.10.0", "numpy>=1.21.0", "pandas>=1.3.0", 
            "scikit-learn>=1.0.0", "joblib>=1.1.0"
        ])
        print("✅ TensorFlow 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ TensorFlow 설치 실패: {e}")
        return False

def check_tensorflow():
    """TensorFlow 설치 확인"""
    try:
        import tensorflow as tf  # type: ignore
        print(f"✅ TensorFlow 설치 확인: {tf.__version__}")
        
        # GPU 확인
        gpus = tf.config.list_physical_devices('GPU')  # type: ignore
        if gpus:
            print(f"✅ GPU 사용 가능: {len(gpus)}개")
            for gpu in gpus:
                print(f"   - {gpu}")
        else:
            print("ℹ️  GPU 없음 (CPU 모드로 실행)")
        
        return True
    except ImportError:
        print("❌ TensorFlow가 설치되지 않았습니다.")
        return False

def test_ai_models():
    """AI 모델 테스트"""
    try:
        print("🧪 AI 모델 테스트 중...")
        
        # TensorFlow 유틸리티 테스트
        from ai_models.tensorflow_utils import (
            TENSORFLOW_AVAILABLE, initialize_tensorflow, get_tensorflow_info
        )
        
        if TENSORFLOW_AVAILABLE:
            initialize_tensorflow()
            info = get_tensorflow_info()
            print(f"✅ TensorFlow 정보: {info}")
            
            # 간단한 모델 생성 테스트
            import tensorflow as tf  # type: ignore
            model = tf.keras.Sequential([  # type: ignore
                tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),  # type: ignore
                tf.keras.layers.Dense(1)  # type: ignore
            ])
            model.compile(optimizer='adam', loss='mse')  # type: ignore
            print("✅ 모델 생성 테스트 성공")
            
        else:
            print("❌ TensorFlow를 사용할 수 없습니다.")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ AI 모델 테스트 실패: {e}")
        return False

def setup_ai_directory():
    """AI 모델 디렉토리 설정"""
    try:
        # 모델 저장 디렉토리 생성
        model_dir = Path("ai_models/saved_models")
        model_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 모델 저장 디렉토리 생성: {model_dir}")
        
        # 로그 디렉토리 생성
        log_dir = Path("logs/ai")
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 로그 디렉토리 생성: {log_dir}")
        
        return True
    except Exception as e:
        print(f"❌ 디렉토리 설정 실패: {e}")
        return False

def main():
    """메인 설정 함수"""
    print("🚀 AI 환경 설정 시작")
    print("=" * 50)
    
    # 1. Python 버전 확인
    if not check_python_version():
        return False
    
    # 2. TensorFlow 확인
    if not check_tensorflow():
        print("\n📦 TensorFlow 설치가 필요합니다.")
        response = input("TensorFlow를 설치하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            if not install_tensorflow():
                return False
            if not check_tensorflow():
                return False
        else:
            print("TensorFlow 없이 기본 기능만 사용합니다.")
    
    # 3. 디렉토리 설정
    if not setup_ai_directory():
        return False
    
    # 4. AI 모델 테스트
    if not test_ai_models():
        print("⚠️  AI 모델 테스트 실패 (기본 기능은 사용 가능)")
    
    print("\n" + "=" * 50)
    print("✅ AI 환경 설정 완료!")
    print("\n📋 사용 가능한 AI 모델:")
    print("   - 매출 예측 (SalesPredictionModel)")
    print("   - 직원 최적화 (StaffOptimizationModel)")
    print("   - 재고 예측 (InventoryForecastingModel)")
    print("   - 고객 분석 (CustomerAnalyticsModel)")
    
    print("\n🔧 사용 방법:")
    print("   from ai_models import create_model")
    print("   model = create_model('sales_prediction')")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 