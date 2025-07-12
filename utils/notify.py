"""
알림 시스템
"""

import json
import logging
import smtplib
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for
from sqlalchemy import and_

from extensions import db
from models import Notification, User
from utils.logger import log_action, log_error

logger = logging.getLogger(__name__)

class NotificationService:
    """알림 서비스 클래스"""

    def __init__(self):
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
        }

        self.kakao_config = {
            "api_url": "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            "access_token": "your-kakao-access-token",
        }

    def send_email(self, to_email, subject, message, html_content=None):
        """이메일 발송"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_config["username"]
            msg["To"] = to_email

            # 텍스트 버전
            text_part = MIMEText(message, "plain", "utf-8")
            msg.attach(text_part)

            # HTML 버전 (있는 경우)
            if html_content:
                html_part = MIMEText(html_content, "html", "utf-8")
                msg.attach(html_part)

            # SMTP 서버 연결 및 발송
            server = smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            )
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            server.send_message(msg)
            server.quit()

            return True, "이메일 발송 성공"

        except Exception as e:
            return False, f"이메일 발송 실패: {str(e)}"

    def send_kakao_message(self, user_id, message):
        """카카오톡 메시지 발송"""
        try:
            headers = {"Authorization": f'Bearer {self.kakao_config["access_token"]}'}

            data = {
                "template_object": json.dumps(
                    {
                        "object_type": "text",
                        "text": message,
                        "link": {
                            "web_url": "https://your-your_program-app.com",
                            "mobile_web_url": "https://your-your_program-app.com",
                        },
                    }
                )
            }

            response = requests.post(
                self.kakao_config["api_url"], headers=headers, data=data
            )

            if response.status_code == 200:
                return True, "카카오톡 발송 성공"
            else:
                return False, f"카카오톡 발송 실패: {response.text}"

        except Exception as e:
            return False, f"카카오톡 발송 실패: {str(e)}"

    def send_sms(self, phone_number, message):
        """SMS 발송 (가상)"""
        try:
            # 실제 SMS API 연동 시 여기에 구현
            # 예: 네이버 클라우드 플랫폼, 가비아 등
            logger.info(f"[SMS] {phone_number}: {message}")
            return True, "SMS 발송 성공 (가상)"

        except Exception as e:
            return False, f"SMS 발송 실패: {str(e)}"


def send_notification(
    user_id, content, related_url=None, email_info=None, kakao_info=None
):
    """
    사용자에게 알림을 생성하고 전송합니다.
    """
    try:
        # 1. 데이터베이스에 알림 저장
        notification = Notification()
        notification.user_id = user_id
        notification.content = content
        notification.related_url = related_url
        notification.created_at = datetime.utcnow()
        db.session.add(notification)
        db.session.commit()

        # 2. 이메일 연동 (주석 처리)
        # if email_info and email_info.get('to'):
        #     # send_email(
        #     #     recipient=email_info['to'],
        #     #     subject=email_info.get('subject', '알림'),
        #     #     template=email_info.get('template', 'default_email'),
        #     #     context={'content': content}
        #     # )
        #     logger.debug(f"이메일 전송 -> {email_info['to']}, 내용: {content}")

        # 3. 카카오톡 연동 (주석 처리)
        # if kakao_info and kakao_info.get('to'):
        #     # send_kakao(
        #     #     recipient=kakao_info['to'],
        #     #     template_code=kakao_info['template_code'],
        #     #     params={'content': content}
        #     # )
        #     logger.debug(f"카카오톡 전송 -> {kakao_info['to']}, 내용: {content}")

    except Exception as e:
        logger.error(f"알림 생성 중 오류 발생: {e}")
        db.session.rollback()


def notify_admins(content, related_url=None):
    """
    Sends a notification to all administrators.
    """
    try:
        admins = User.query.filter_by(role="admin").all()
        for admin in admins:
            send_notification(admin.id, content, related_url)
    except Exception as e:
        logger.error(f"Error sending admin notifications: {e}")


def send_sms(user, message):
    try:
        logger.info(f"[SMS] to {getattr(user, 'phone', '-')}: {message}")
        # 실제 SMS 연동은 아래 주석 해제
        # ...
        return True
    except Exception as e:
        logger.error(f"SMS 예외: {e}")
        return True


def notify_salary_payment(user, amount, year, month):
    """급여 지급 알림"""
    message = f"""
{user.name or user.username}님,

{year}년 {month}월 급여가 지급되었습니다.

지급 금액: {amount:,}원
지급 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

문의사항이 있으시면 관리자에게 연락해 주세요.

감사합니다.
레스토랑 관리 시스템
    """.strip()

    # 이메일 알림
    if user.email:
        send_notification(
            user.id, message, url_for("salary_payment", year=year, month=month)
        )

    # SMS 알림 (선택사항)
    if user.phone:
        sms_message = f"{year}년{month}월 급여 {amount:,}원이 입금되었습니다."
        send_notification(
            user.id, sms_message, url_for("salary_payment", year=year, month=month)
        )


def notify_attendance_issue(user, year, month, lateness, early_leave, night_work):
    """근태 이상 알림"""
    issues = []
    if lateness > 0:
        issues.append(f"지각 {lateness}회")
    if early_leave > 0:
        issues.append(f"조퇴 {early_leave}회")
    if night_work > 0:
        issues.append(f"야근 {night_work}회")

    if issues:
        message = f"""
{user.name or user.username}님,

{year}년 {month}월 근태 현황을 알려드립니다.

발생 이슈: {', '.join(issues)}

근태 개선을 위해 노력해 주시기 바랍니다.

감사합니다.
레스토랑 관리 시스템
        """.strip()

        send_notification(
            user.id, message, url_for("attendance_issue", year=year, month=month)
        )


def notify_approval_result(user, approved):
    """승인 결과 알림"""
    if approved:
        message = f"""
{user.name or user.username}님,

회원가입이 승인되었습니다!

이제 시스템에 로그인하여 사용하실 수 있습니다.
로그인: https://your-your_program-app.com/login

감사합니다.
레스토랑 관리 시스템
        """.strip()
    else:
        message = f"""
{user.name or user.username}님,

회원가입 신청이 거절되었습니다.

자세한 사유는 관리자에게 문의해 주세요.

감사합니다.
레스토랑 관리 시스템
        """.strip()

    send_notification(user.id, message, url_for("approval_result", approved=approved))


def notify_system_maintenance(message, users=None):
    """시스템 점검 알림"""
    if users is None:
        users = User.query.filter_by(status="approved").all()

    for user in users:
        send_notification(user.id, message, url_for("system_maintenance"))


def notify_holiday_reminder(user, holiday_date, holiday_name):
    """공휴일 알림"""
    message = f"""
{user.name or user.username}님,

다음 공휴일을 안내드립니다.

공휴일: {holiday_date}
공휴명: {holiday_name}

공휴일 근무가 필요한 경우 미리 알려주세요.

감사합니다.
레스토랑 관리 시스템
    """.strip()

    send_notification(
        user.id, message, url_for("holiday_reminder", holiday_date=holiday_date)
    )


def notify_birthday(user):
    """생일 축하 알림"""
    message = f"""
{user.name or user.username}님,

생일을 축하드립니다! 🎉

오늘 하루도 즐겁게 보내세요.
레스토랑에서 함께 일할 수 있어서 기쁩니다.

감사합니다.
레스토랑 관리 시스템
    """.strip()

    send_notification(user.id, message, url_for("birthday"))


def log_notification(user_id, notification_type, message, success, error_msg=""):
    """알림 로그 기록"""
    try:
        log_action(
            user_id,
            f"NOTIFICATION_{notification_type.upper()}",
            f"{'SUCCESS' if success else 'FAILED'}: {message} {error_msg}",
        )
    except Exception as e:
        logger.error(f"알림 로그 기록 실패: {e}")


def send_notification_enhanced(user_id, content, category="공지", link=None):
    """
    개선된 알림 생성 함수
    Args:
        user_id: 사용자 ID
        content: 알림 내용
        category: 카테고리 ('발주', '청소', '근무', '교대', '공지' 등)
        link: 상세 페이지 링크
    """
    try:
        n = Notification()
        n.user_id = user_id
        n.content = content
        n.category = category
        n.link = link
        db.session.add(n)
        db.session.commit()

        log_notification(user_id, category, content, True)
        return True, "알림 생성 성공"

    except Exception as e:
        db.session.rollback()
        log_notification(user_id, category, content, False, str(e))
        return False, f"알림 생성 실패: {str(e)}"


def send_notification_to_user(user, content, category="공지", link=None):
    """
    User 객체를 받아서 알림 생성
    """
    return send_notification_enhanced(user.id, content, category, link)


def send_notification_to_multiple_users(user_ids, content, category="공지", link=None):
    """
    여러 사용자에게 동일한 알림 발송
    """
    success_count = 0
    for user_id in user_ids:
        success, _ = send_notification_enhanced(user_id, content, category, link)
        if success:
            success_count += 1

    return success_count, len(user_ids)


# 특정 상황별 알림 함수들
def notify_order_approval(order):
    """발주 승인 알림"""
    content = f"발주 '{order.item}' ({order.quantity}개)가 승인되었습니다."
    link = f"/order_detail/{order.id}"
    return send_notification_enhanced(order.ordered_by, content, "발주", link)


def notify_order_rejection(order, reason=""):
    """발주 거절 알림"""
    content = f"발주 '{order.item}' ({order.quantity}개)가 거절되었습니다."
    if reason:
        content += f" 사유: {reason}"
    link = f"/order_detail/{order.id}"
    return send_notification_enhanced(order.ordered_by, content, "발주", link)


def notify_shift_approval(schedule):
    """교대 승인 알림"""
    content = f"{schedule.date.strftime('%m월 %d일')} 교대 신청이 승인되었습니다."
    link = "/swap_manage"
    return send_notification_enhanced(schedule.user_id, content, "교대", link)


def notify_shift_rejection(schedule, reason=""):
    """교대 거절 알림"""
    content = f"{schedule.date.strftime('%m월 %d일')} 교대 신청이 거절되었습니다."
    if reason:
        content += f" 사유: {reason}"
    link = "/swap_manage"
    return send_notification_enhanced(schedule.user_id, content, "교대", link)


def notify_cleaning_assignment(cleaning_plan):
    """청소 배정 알림"""
    content = f"{cleaning_plan.date.strftime('%m월 %d일')} 청소 담당으로 배정되었습니다: {cleaning_plan.plan}"
    link = "/clean"
    return send_notification_enhanced(cleaning_plan.user_id, content, "청소", link)


def notify_schedule_change(schedule):
    """근무 일정 변경 알림"""
    content = f"{schedule.date.strftime('%m월 %d일')} 근무 일정이 변경되었습니다: {schedule.start_time.strftime('%H:%M')}~{schedule.end_time.strftime('%H:%M')}"
    link = "/schedule"
    return send_notification_enhanced(schedule.user_id, content, "근무", link)


def notify_new_notice(notice, target_users=None):
    """새 공지사항 알림"""
    content = f"새 공지사항: {notice.title}"
    link = f"/notice_view/{notice.id}"

    if target_users:
        # 특정 사용자들에게만 발송
        for user in target_users:
            send_notification_enhanced(user.id, content, "공지", link)
    else:
        # 모든 승인된 사용자에게 발송
        users = User.query.filter_by(status="approved").all()
        for user in users:
            send_notification_enhanced(user.id, content, "공지", link)


def notify_attendance_reminder(user, date):
    """출근 알림"""
    content = f"{date.strftime('%m월 %d일')} 출근 시간입니다. 출근 처리를 해주세요."
    link = "/attendance"
    return send_notification_enhanced(user.id, content, "근무", link)


def notify_system_announcement(message, category="공지", target_users=None):
    """시스템 공지 알림"""
    if target_users:
        for user in target_users:
            send_notification_enhanced(user.id, message, category, None)
    else:
        users = User.query.filter_by(status="approved").all()
        for user in users:
            send_notification_enhanced(user.id, message, category, None)


# 글로벌 알림 서비스 인스턴스
notification_service = NotificationService()


def send_order_approval_notification(order):
    """발주 승인 시 담당 매니저와 발주자 모두에게 알림"""
    try:
        # 발주자에게 알림
        send_notification_enhanced(
            order.ordered_by,
            f"발주 '{order.item}' ({order.quantity}개)가 승인되었습니다.",
            "발주",
            f"/order_detail/{order.id}",
        )

        # 매니저(관리자) 전체에게도 알림
        managers = User.query.filter(User.role.in_(["admin", "manager"])).all()
        for manager in managers:
            if manager.id != order.ordered_by:  # 발주자와 다른 경우만
                send_notification_enhanced(
                    manager.id,
                    f"발주 '{order.item}' ({order.quantity}개)가 승인 처리되었습니다. (발주자: {order.user.username})",
                    "발주",
                    f"/order_detail/{order.id}",
                )

        return True
    except Exception as e:
        logger.error(f"발주 승인 알림 발송 실패: {e}")
        return False


def send_admin_only_notification(content, category="공지", link=None):
    """관리자만 볼 수 있는 시스템 알림"""
    try:
        admins = User.query.filter_by(role="admin").all()
        for admin in admins:
            notification = Notification()
            notification.user_id = admin.id
            notification.content = content
            notification.category = category
            notification.link = link
            notification.is_admin_only = True
            db.session.add(notification)

        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"관리자 전용 알림 발송 실패: {e}")
        db.session.rollback()
        return False


def send_notification_to_role(
    role, content, category="공지", link=None, is_admin_only=False
):
    """특정 역할의 사용자들에게 알림 발송"""
    try:
        users = User.query.filter_by(role=role).all()
        for user in users:
            notification = Notification()
            notification.user_id = user.id
            notification.content = content
            notification.category = category
            notification.link = link
            notification.is_admin_only = is_admin_only
            db.session.add(notification)

        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"역할별 알림 발송 실패: {e}")
        db.session.rollback()
        return False


def send_notification_with_keyword_filter(keyword, content, category="공지", link=None):
    """키워드가 포함된 알림을 받은 사용자들에게 추가 알림 발송"""
    try:
        # 키워드가 포함된 알림을 받은 사용자들 찾기
        users_with_keyword = (
            db.session.query(Notification.user_id)
            .filter(Notification.content.contains(keyword))
            .distinct()
            .all()
        )

        user_ids = [user_id[0] for user_id in users_with_keyword]

        for user_id in user_ids:
            send_notification_enhanced(user_id, content, category, link)

        return True
    except Exception as e:
        logger.error(f"키워드 필터 알림 발송 실패: {e}")
        return False


def send_kakao(user, message):
    # 실제 연동은 나중에! 현재는 아무 동작 안 함
    pass


def send_email(user, subject, body, attachment=None):
    # 실제 연동은 나중에! 현재는 아무 동작 안 함
    pass


def send_notification_simple(user, message):
    # 실제 카카오톡/이메일/SMS API 연동 위치
    # 예: requests.post 또는 SMTP, 문자 발송 등
    logger.info(f"[알림] to {user.name or user.username}: {message}")
    return True

