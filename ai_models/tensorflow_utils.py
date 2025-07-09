"""
TensorFlow 공통 유틸리티
모든 AI 모델에서 사용하는 안전한 TensorFlow import 및 타입 처리
"""

import logging
from typing import Optional, Any, TYPE_CHECKING, Union

# TensorFlow 조건부 import
TENSORFLOW_AVAILABLE = False
tf: Optional[Any] = None

try:
    import tensorflow as tf  # type: ignore
    TENSORFLOW_AVAILABLE = True
    print("TensorFlow 로드 성공")
except ImportError:
    print("TensorFlow가 설치되지 않았습니다. AI 기능을 사용하려면 TensorFlow를 설치하세요.")
    print("설치 명령어: pip install tensorflow")

# 타입 체킹 시에만 TensorFlow 타입 사용
if TYPE_CHECKING:
    try:
        import tensorflow as tf  # type: ignore
    except ImportError:
        tf = None

def check_tensorflow_available():
    """TensorFlow 사용 가능 여부 확인"""
    if not TENSORFLOW_AVAILABLE:
        raise ImportError(
            "TensorFlow가 필요합니다. 다음 명령어로 설치하세요:\n"
            "pip install tensorflow\n"
            "또는\n"
            "conda install tensorflow"
        )
    return True

def get_tensorflow():
    """안전한 TensorFlow 객체 반환"""
    check_tensorflow_available()
    return tf

def create_sequential_model(layers_config):
    """안전한 Sequential 모델 생성"""
    check_tensorflow_available()
    
    if tf is None:
        raise ImportError("TensorFlow가 로드되지 않았습니다.")
    
    model = tf.keras.Sequential()  # type: ignore
    for layer_config in layers_config:
        layer_type = layer_config['type']
        params = layer_config.get('params', {})
        
        if layer_type == 'Input':
            model.add(tf.keras.Input(**params))  # type: ignore
        elif layer_type == 'Dense':
            model.add(tf.keras.layers.Dense(**params))  # type: ignore
        elif layer_type == 'LSTM':
            model.add(tf.keras.layers.LSTM(**params))  # type: ignore
        elif layer_type == 'Dropout':
            model.add(tf.keras.layers.Dropout(**params))  # type: ignore
        elif layer_type == 'Conv1D':
            model.add(tf.keras.layers.Conv1D(**params))  # type: ignore
        elif layer_type == 'MaxPooling1D':
            model.add(tf.keras.layers.MaxPooling1D(**params))  # type: ignore
        elif layer_type == 'Flatten':
            model.add(tf.keras.layers.Flatten(**params))  # type: ignore
        else:
            raise ValueError(f"지원하지 않는 레이어 타입: {layer_type}")
    
    return model

def create_callbacks(model_path, monitor='val_loss', patience=10):
    """표준 콜백 생성"""
    check_tensorflow_available()
    
    if tf is None:
        raise ImportError("TensorFlow가 로드되지 않았습니다.")
    
    callbacks = [
        tf.keras.callbacks.EarlyStopping(  # type: ignore
            patience=patience, 
            restore_best_weights=True,
            monitor=monitor
        ),
        tf.keras.callbacks.ReduceLROnPlateau(  # type: ignore
            factor=0.5, 
            patience=5,
            monitor=monitor
        ),
        tf.keras.callbacks.ModelCheckpoint(  # type: ignore
            model_path, 
            save_best_only=True, 
            monitor=monitor
        )
    ]
    
    return callbacks

def compile_model(model, optimizer='adam', loss='mse', metrics=None):
    """모델 컴파일"""
    check_tensorflow_available()
    
    if tf is None:
        raise ImportError("TensorFlow가 로드되지 않았습니다.")
    
    if metrics is None:
        metrics = ['mae']
    
    if optimizer == 'adam':
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)  # type: ignore
    
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metrics
    )
    
    return model

def load_model_safely(model_path):
    """안전한 모델 로드"""
    check_tensorflow_available()
    
    if tf is None:
        raise ImportError("TensorFlow가 로드되지 않았습니다.")
    
    try:
        model = tf.keras.models.load_model(model_path)  # type: ignore
        return model
    except Exception as e:
        raise RuntimeError(f"모델 로드 실패: {e}")

def save_model_safely(model, model_path):
    """안전한 모델 저장"""
    check_tensorflow_available()
    
    # .keras 확장자 사용 권장
    if model_path.endswith('.h5'):
        model_path = model_path.replace('.h5', '.keras')
    elif not model_path.endswith('.keras'):
        model_path = model_path + '.keras'
    try:
        model.save(model_path)
        return True
    except Exception as e:
        raise RuntimeError(f"모델 저장 실패: {e}")

# 로깅 설정
def setup_ai_logging():
    """AI 모델용 로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# TensorFlow 버전 정보
def get_tensorflow_info():
    """TensorFlow 버전 및 정보 반환"""
    if TENSORFLOW_AVAILABLE and tf is not None:
        return {
            'version': tf.__version__,  # type: ignore
            'available': True,
            'gpu_available': len(tf.config.list_physical_devices('GPU')) > 0  # type: ignore
        }
    else:
        return {
            'version': None,
            'available': False,
            'gpu_available': False
        }

# 모델 요약 정보
def print_model_summary(model):
    """모델 요약 출력"""
    check_tensorflow_available()
    
    try:
        model.summary()
    except Exception as e:
        print(f"모델 요약 출력 실패: {e}")

# GPU 메모리 관리
def setup_gpu_memory_growth():
    """GPU 메모리 증가 설정"""
    if TENSORFLOW_AVAILABLE and tf is not None:
        try:
            gpus = tf.config.experimental.list_physical_devices('GPU')  # type: ignore
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)  # type: ignore
                print("GPU 메모리 증가 설정 완료")
        except Exception as e:
            print(f"GPU 설정 실패: {e}")

# 초기화 함수
def initialize_tensorflow():
    """TensorFlow 초기화"""
    if TENSORFLOW_AVAILABLE:
        setup_gpu_memory_growth()
        info = get_tensorflow_info()
        print(f"TensorFlow 초기화 완료: {info}")
        return True
    else:
        print("TensorFlow가 설치되지 않아 초기화를 건너뜁니다.")
        return False 