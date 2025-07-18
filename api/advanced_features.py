import base64
from datetime import datetime
import logging
from utils.decorators import admin_required, manager_required  # pyright: ignore
from utils.translation_manager import translation_manager  # pyright: ignore
from utils.image_analyzer import image_analyzer  # pyright: ignore
from utils.voice_manager import voice_manager  # pyright: ignore
from utils.chatbot_manager import chatbot_manager  # pyright: ignore
import os
import sys
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

advanced_features = Blueprint('advanced_features', __name__)


@advanced_features.app_errorhandler(Exception)
def handle_global_exception(error):
    current_app.logger.error(f"[공통 예외] {str(error)}")
    return jsonify({
        'error': '서버 내부 오류가 발생했습니다.',
        'details': str(error)
    }), 500


def handle_advanced_error(func):
    """고급 기능 API 에러 핸들러 데코레이터"""
    @wraps(func)
    def wrapper(*args,  **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Advanced features API 에러: {str(e)}")
            return jsonify({
                "error": "고급 기능 처리 중 오류가 발생했습니다.",
                "details": str(e)
            }), 500
    return wrapper

# ==================== 챗봇 API ====================


@advanced_features.route('/chatbot/message', methods=['POST'])
@login_required
@handle_advanced_error
def chatbot_message():
    """챗봇 메시지 처리"""
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "메시지가 필요합니다."}), 400

    message = data['message'] if data is not None else None
    user_id = current_user.id

    if message is None:
        return jsonify({"error": "메시지가 필요합니다."}), 400
    # 챗봇 처리
    chat_message = chatbot_manager.process_message(user_id, message)

    return jsonify({
        "success": True,
        "response": chat_message.response,
        "intent": chat_message.intent,
        "confidence": chat_message.confidence,
        "entities": chat_message.entities,
        "timestamp": chat_message.timestamp.isoformat()
    })


@advanced_features.route('/chatbot/history', methods=['GET'])
@login_required
@handle_advanced_error
def chatbot_history():
    """챗봇 대화 히스토리"""
    user_id = current_user.id
    limit = request.args.get('limit', default=10, type=int)

    history = chatbot_manager.get_conversation_history(user_id, limit)

    return jsonify({
        "success": True,
        "history": [
            {
                "message": msg.message,
                "response": msg.response,
                "intent": msg.intent,
                "timestamp": msg.timestamp.isoformat()
            } for msg in history
        ]
    })


@advanced_features.route('/chatbot/clear', methods=['POST'])
@login_required
@handle_advanced_error
def chatbot_clear():
    """챗봇 대화 초기화"""
    user_id = current_user.id
    chatbot_manager.clear_context(user_id)

    return jsonify({
        "success": True,
        "message": "대화가 초기화되었습니다."
    })


@advanced_features.route('/chatbot/stats', methods=['GET'])
@login_required
@admin_required
@handle_advanced_error
def chatbot_stats():
    """챗봇 통계"""
    stats = chatbot_manager.get_chat_statistics()

    return jsonify({
        "success": True,
        "stats": stats
    })

# ==================== 음성 인식 API ====================


@advanced_features.route('/voice/process', methods=['POST'])
@login_required
@handle_advanced_error
def voice_process():
    """음성 처리"""
    data = request.get_json()

    if not data or 'audio_data' not in data:
        return jsonify({"error": "오디오 데이터가 필요합니다."}), 400

    try:
        # Base64 디코딩
        audio_data_b64 = data['audio_data'] if data is not None else None
        if audio_data_b64 is None:
            return jsonify({"error": "오디오 데이터가 필요합니다."}), 400
        audio_data = base64.b64decode(audio_data_b64)
        user_id = current_user.id
        # 음성 처리
        voice_command = voice_manager.process_audio(audio_data, user_id)
        # 명령 실행
        response = voice_manager.execute_command(voice_command)
        return jsonify({
            "success": True,
            "text": voice_command.text,
            "command_type": voice_command.command_type,
            "confidence": voice_command.confidence,
            "response": response,
            "timestamp": voice_command.timestamp.isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"음성 처리 실패: {str(e)}"}), 400


@advanced_features.route('/voice/tts', methods=['POST'])
@login_required
@handle_advanced_error
def text_to_speech():
    """텍스트를 음성으로 변환"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "텍스트가 필요합니다."}), 400

    text = data['text'] if data is not None else None
    user_id = current_user.id

    if text is None:
        return jsonify({"error": "텍스트가 필요합니다."}), 400
    # TTS 처리
    audio_data = voice_manager.text_to_speech(text,  user_id)

    # Base64 인코딩
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    return jsonify({
        "success": True,
        "audio_data": audio_base64,
        "text": text
    })


@advanced_features.route('/voice/stats', methods=['GET'])
@login_required
@admin_required
@handle_advanced_error
def voice_stats():
    """음성 명령 통계"""
    stats = voice_manager.get_voice_statistics()

    return jsonify({
        "success": True,
        "stats": stats
    })

# ==================== 이미지 분석 API ====================


@advanced_features.route('/image/analyze', methods=['POST'])
@login_required
@handle_advanced_error
def image_analyze():
    """이미지 분석"""
    data = request.get_json()

    if not data or 'image_data' not in data or 'analysis_types' not in data:
        return jsonify({"error": "이미지 데이터와 분석 타입이 필요합니다."}), 400

    try:
        # Base64 디코딩
        image_data_b64 = data['image_data'] if data is not None else None
        if image_data_b64 is None:
            return jsonify({"error": "이미지 데이터가 필요합니다."}), 400
        image_data = base64.b64decode(image_data_b64)
        analysis_types = data['analysis_types'] if data is not None else None
        # 이미지 분석
        results = image_analyzer.analyze_image(image_data, analysis_types)

        return jsonify({
            "success": True,
            "results": [
                {
                    "analysis_type": result.analysis_type,
                    "confidence": result.confidence,
                    "results": result.results,
                    "processing_time": result.processing_time,
                    "timestamp": result.timestamp.isoformat()
                } for result in results
            ]
        })

    except Exception as e:
        return jsonify({"error": f"이미지 분석 실패: {str(e)}"}), 400


@advanced_features.route('/image/receipt', methods=['POST'])
@login_required
@handle_advanced_error
def process_receipt():
    """영수증 처리"""
    data = request.get_json()

    if not data or 'image_data' not in data:
        return jsonify({"error": "이미지 데이터가 필요합니다."}), 400

    try:
        # Base64 디코딩
        image_data_b64 = data['image_data'] if data is not None else None
        if image_data_b64 is None:
            return jsonify({"error": "이미지 데이터가 필요합니다."}), 400
        image_data = base64.b64decode(image_data_b64)
        # 영수증 처리
        receipt_info = image_analyzer.process_receipt(image_data)

        return jsonify({
            "success": True,
            "receipt_info": receipt_info
        })

    except Exception as e:
        return jsonify({"error": f"영수증 처리 실패: {str(e)}"}), 400


@advanced_features.route('/image/stats', methods=['GET'])
@login_required
@admin_required
@handle_advanced_error
def image_stats():
    """이미지 분석 통계"""
    stats = image_analyzer.get_analysis_statistics()

    return jsonify({
        "success": True,
        "stats": stats
    })

# ==================== 번역 API ====================


@advanced_features.route('/translate/text', methods=['POST'])
@login_required
@handle_advanced_error
def translate_text():
    """텍스트 번역"""
    data = request.get_json()

    if not data or 'text' not in data or 'target_language' not in data:
        return jsonify({"error": "텍스트와 대상 언어가 필요합니다."}), 400

    text = data['text'] if data is not None else None
    target_language = data['target_language'] if data is not None else None
    source_language = data.get('source_language') if data else None

    if text is None or target_language is None:
        return jsonify({"error": "텍스트와 대상 언어가 필요합니다."}), 400
    # 번역 수행
    result = translation_manager.translate_text(text,  target_language,  source_language)

    return jsonify({
        "success": True,
        "translated_text": result.translated_text,
        "source_language": result.source_language,
        "target_language": result.target_language,
        "confidence": result.confidence,
        "processing_time": result.processing_time,
        "timestamp": result.timestamp.isoformat()
    })


@advanced_features.route('/translate/menu', methods=['POST'])
@login_required
@handle_advanced_error
def translate_menu():
    """메뉴 번역"""
    data = request.get_json()

    if not data or 'menu_items' not in data or 'target_language' not in data:
        return jsonify({"error": "메뉴 항목과 대상 언어가 필요합니다."}), 400

    menu_items = data['menu_items'] if data is not None else None
    target_language = data['target_language'] if data is not None else None

    if menu_items is None or target_language is None:
        return jsonify({"error": "메뉴 항목과 대상 언어가 필요합니다."}), 400
    # 메뉴 번역
    translated_menu = translation_manager.translate_menu(menu_items,  target_language)

    return jsonify({
        "success": True,
        "translated_menu": translated_menu
    })


@advanced_features.route('/translate/notification', methods=['POST'])
@login_required
@handle_advanced_error
def translate_notification():
    """알림 번역"""
    data = request.get_json()

    if not data or 'notification' not in data or 'target_language' not in data:
        return jsonify({"error": "알림과 대상 언어가 필요합니다."}), 400

    notification = data['notification'] if data is not None else None
    target_language = data['target_language'] if data is not None else None

    if notification is None or target_language is None:
        return jsonify({"error": "알림과 대상 언어가 필요합니다."}), 400
    # 알림 번역
    translated_notification = translation_manager.translate_notification(notification,  target_language)

    return jsonify({
        "success": True,
        "translated_notification": translated_notification
    })


@advanced_features.route('/translate/batch', methods=['POST'])
@login_required
@handle_advanced_error
def batch_translate():
    """배치 번역"""
    data = request.get_json()

    if not data or 'texts' not in data or 'target_language' not in data:
        return jsonify({"error": "텍스트 목록과 대상 언어가 필요합니다."}), 400

    texts = data['texts'] if data is not None else None
    target_language = data['target_language'] if data is not None else None
    source_language = data.get('source_language') if data else None

    if target_language is None:
        return jsonify({"error": "대상 언어가 필요합니다."}), 400

    # 배치 번역
    results = translation_manager.batch_translate(texts,  target_language,  source_language)

    return jsonify({
        "success": True,
        "results": [
            {
                "translated_text": result.translated_text,
                "confidence": result.confidence,
                "processing_time": result.processing_time
            } for result in results
        ]
    })


@advanced_features.route('/translate/languages', methods=['GET'])
@handle_advanced_error
def get_supported_languages():
    """지원 언어 목록"""
    languages = translation_manager.supported_languages

    return jsonify({
        "success": True,
        "languages": languages
    })


@advanced_features.route('/translate/detect', methods=['POST'])
@login_required
@handle_advanced_error
def detect_language():
    """언어 감지"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "텍스트가 필요합니다."}), 400

    text = data['text'] if data is not None else None
    if text is None:
        return jsonify({"error": "텍스트가 필요합니다."}), 400

    # 언어 감지
    detected_lang, confidence = translation_manager.detect_language(text)

    return jsonify({
        "success": True,
        "detected_language": detected_lang,
        "confidence": confidence,
        "language_name": translation_manager.supported_languages.get(detected_lang, "Unknown")
    })


@advanced_features.route('/translate/stats', methods=['GET'])
@login_required
@admin_required
@handle_advanced_error
def translation_stats():
    """번역 통계"""
    stats = translation_manager.get_translation_statistics()

    return jsonify({
        "success": True,
        "stats": stats
    })

# ==================== 통합 API ====================


@advanced_features.route('/integrated/process', methods=['POST'])
@login_required
@handle_advanced_error
def integrated_process():
    """통합 처리 (음성 + 이미지 + 번역)"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "데이터가 필요합니다."}), 400

    results = {}

    # 음성 처리
    if 'audio_data' in data:
        try:
            audio_data_b64 = data['audio_data'] if data is not None else None
            if audio_data_b64 is None:
                return jsonify({"error": "오디오 데이터가 필요합니다."}), 400
            audio_data = base64.b64decode(audio_data_b64)
            voice_command = voice_manager.process_audio(audio_data, current_user.id)
            voice_response = voice_manager.execute_command(voice_command)

            # 번역이 요청된 경우
            if 'translate_to' in data:
                translate_to = data['translate_to'] if data is not None else None
                if translate_to is None:
                    return jsonify({"error": "번역 대상 언어가 필요합니다."}), 400
                translated_response = translation_manager.translate_text(
                    voice_response, translate_to, 'ko'
                ).translated_text
                results['voice'] = {
                    "original_text": voice_command.text,
                    "original_response": voice_response,
                    "translated_response": translated_response
                }
            else:
                results['voice'] = {
                    "text": voice_command.text,
                    "response": voice_response
                }
        except Exception as e:
            results['voice'] = {"error": str(e)}

    # 이미지 처리
    if 'image_data' in data:
        try:
            image_data_b64 = data['image_data'] if data is not None else None
            if image_data_b64 is None:
                return jsonify({"error": "이미지 데이터가 필요합니다."}), 400
            image_data = base64.b64decode(image_data_b64)
            analysis_types = data.get('analysis_types', ['qr_code', 'ocr', 'quality'])
            image_results = image_analyzer.analyze_image(image_data, analysis_types)
            results['image'] = [
                {
                    "type": result.analysis_type,
                    "results": result.results
                } for result in image_results
            ]
        except Exception as e:
            results['image'] = {"error": str(e)}

    return jsonify({
        "success": True,
        "results": results
    })
