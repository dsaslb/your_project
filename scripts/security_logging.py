import logging
from logging.handlers import RotatingFileHandler
import os


def setup_security_logging():
    """蹂댁븞 濡쒓퉭 ?ㅼ젙"""
    # 濡쒓렇 ?붾젆?좊━ ?앹꽦
    os.makedirs("logs/security", exist_ok=True)

    # 蹂댁븞 濡쒓굅 ?ㅼ젙
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)

    # ?뚯씪 ?몃뱾??(?쇰퀎 濡쒗뀒?댁뀡)
    file_handler = RotatingFileHandler(
        "logs/security/security.log", maxBytes=10 * 1024 * 1024, backupCount=30  # 10MB
    )
    file_handler.setLevel(logging.INFO)

    # ?щ㎎??
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    security_logger.addHandler(file_handler)

    return security_logger


# 蹂댁븞 ?대깽??濡쒓퉭 ?⑥닔??
def log_login_attempt(user_id, success, ip_address):
    """濡쒓렇???쒕룄 濡쒓퉭"""
    logger = logging.getLogger("security")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Login attempt: user_id={user_id}, status={status}, ip={ip_address}")


def log_permission_change(user_id, target_user_id, change_type):
    """沅뚰븳 蹂寃?濡쒓퉭"""
    logger = logging.getLogger("security")
    logger.info(
        f"Permission change: user_id={user_id}, target={target_user_id}, type={change_type}"
    )


def log_suspicious_activity(activity_type, details, ip_address):
    """?섏떖?ㅻ윭???쒕룞 濡쒓퉭"""
    logger = logging.getLogger("security")
    logger.warning(
        f"Suspicious activity: type={activity_type}, details={details}, ip={ip_address}"
    )


if __name__ == "__main__":
    logger = setup_security_logging()
    logger.info("Security logging system initialized")
