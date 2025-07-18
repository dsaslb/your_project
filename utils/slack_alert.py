from utils.logger import log_action  # pyright: ignore
import requests
from typing import Optional
import os
import logging
form = None  # pyright: ignore
"""Slack Webhook을 통한 알림 시스템"""


logger = logging.getLogger(__name__)

# Slack Webhook URL 환경변수에서 가져오기
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_alert(message: str, level: str = "INFO") -> bool:
    """
    Slack으로 알림 메시지 전송

    Args:
        message: 전송할 메시지
        level: 로그 레벨 (INFO, WARNING, ERROR, CRITICAL)

    Returns:
        bool: 전송 성공 여부
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("❌ Slack Webhook URL이 설정되지 않았습니다.")
        return False

    # 레벨별 이모지 설정
    level_emojis = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "🚨", "CRITICAL": "💥"}

    emoji = level_emojis.get(level.upper(), "ℹ️")

    # Slack 메시지 포맷팅
    formatted_message = f"{emoji} [{level.upper()}] {message}"

    payload = {
        "text": formatted_message,
        "username": "your_program System Bot",
        "icon_emoji": ":your_program:",
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        logger.info(f"Slack 알림 전송 성공: {message[:50] if message is not None else None}...")
        return True

    except requests.exceptions.Timeout:
        logger.error("Slack 알림 전송 타임아웃")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Slack 알림 전송 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"Slack 알림 전송 중 예상치 못한 오류: {e}")
        return False


def send_slack_error_alert(error_message: str, context: Optional[str] = None) -> bool:
    """
    에러 전용 Slack 알림

    Args:
        error_message: 에러 메시지
        context: 추가 컨텍스트 정보

    Returns:
        bool: 전송 성공 여부
    """
    full_message = error_message
    if context:
        full_message += f"\n컨텍스트: {context}"

    return send_slack_alert(full_message, "ERROR")


def send_slack_critical_alert(
    critical_message: str, context: Optional[str] = None
) -> bool:
    """
    심각한 장애 전용 Slack 알림

    Args:
        critical_message: 심각한 장애 메시지
        context: 추가 컨텍스트 정보

    Returns:
        bool: 전송 성공 여부
    """
    full_message = f"🚨 심각한 장애 발생! 🚨\n{critical_message}"
    if context:
        full_message += f"\n컨텍스트: {context}"

    return send_slack_alert(full_message, "CRITICAL")


def test_slack_connection() -> bool:
    """
    Slack 연결 테스트

    Returns:
        bool: 연결 성공 여부
    """
    if not SLACK_WEBHOOK_URL:
        logger.error("❌ Slack Webhook URL이 설정되지 않았습니다.")
        return False

    test_message = "🧪 Slack 연결 테스트 메시지입니다."
    success = send_slack_alert(test_message, "INFO")

    if success:
        logger.info("✅ Slack 연결 테스트 성공!")
    else:
        logger.error("❌ Slack 연결 테스트 실패!")

    return success


def send_event_alert(
    event: str, user: Optional[str] = None, detail: Optional[str] = None, level: str = "INFO"
) -> bool:
    """
    주요 이벤트 Slack 알림

    Args:
        event: 이벤트 종류 (회원가입, 로그인, 권한변경 등)
        user: 관련 사용자
        detail: 상세 정보
        level: 알림 레벨

    Returns:
        bool: 전송 성공 여부
    """
    msg = f"📝 [이벤트] {event}"
    if user:
        msg += f"\n사용자: {user}"
    if detail:
        msg += f"\n상세: {detail}"

    return send_slack_alert(msg, level)


def send_security_alert(
    event: str, user: Optional[str] = None, ip: Optional[str] = None, detail: Optional[str] = None
) -> bool:
    """
    보안 관련 이벤트 Slack 알림

    Args:
        event: 보안 이벤트 종류
        user: 관련 사용자
        ip: IP 주소
        detail: 상세 정보

    Returns:
        bool: 전송 성공 여부
    """
    msg = f"🔒 [보안] {event}"
    if user:
        msg += f"\n사용자: {user}"
    if ip:
        msg += f"\nIP: {ip}"
    if detail:
        msg += f"\n상세: {detail}"

    return send_slack_alert(msg, "WARNING")


def send_data_change_alert(
    event: str,
    user: Optional[str] = None,
    target: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
) -> bool:
    """
    데이터 변경 이벤트 Slack 알림

    Args:
        event: 변경 이벤트 종류
        user: 변경한 사용자
        target: 변경 대상
        old_value: 이전 값
        new_value: 새로운 값

    Returns:
        bool: 전송 성공 여부
    """
    msg = f"📊 [데이터변경] {event}"
    if user:
        msg += f"\n변경자: {user}"
    if target:
        msg += f"\n대상: {target}"
    if old_value and new_value:
        msg += f"\n변경: {old_value} → {new_value}"

    return send_slack_alert(msg, "INFO")


def send_slack_alert_if_prod(message: str, level: str = "INFO") -> bool:
    """
    운영 환경에서만 Slack 알림 전송

    Args:
        message: 전송할 메시지
        level: 로그 레벨

    Returns:
        bool: 전송 성공 여부
    """
    if os.getenv("FLASK_ENV") == "production":
        return send_slack_alert(message, level)
    return False
