"""
자동 담당자 배정 및 SLA 관리 시스템
"""

from datetime import datetime, timedelta
import logging

from sqlalchemy import and_, func, or_

from extensions import db
from models import Attendance, User
from models.notification_models import AttendanceReport
from utils.email_utils import email_service
from utils.logger import log_action, log_error
from utils.notify import send_notification_enhanced

logger = logging.getLogger(__name__)


class AssigneeManager:
    """담당자 배정 관리 클래스"""

    @staticmethod
    def auto_assign_dispute(dispute):
        """신고/이의제기 자동 담당자 배정"""
        try:
            # 현재 업무량이 가장 적은 담당자 찾기
            assignees = User.query.filter(
                and_(
                    User.role.in_(["admin", "manager"]),
                    User.status == "approved",
                    User.deleted_at.is_(None),
                )
            ).all()

            if not assignees:
                return None

            # 담당자별 업무량 계산
            assignee_workloads = []
            for assignee in assignees:
                workload = AssigneeManager.get_assignee_workload(assignee.id)
                assignee_workloads.append(
                    {
                        "assignee_id": assignee.id,
                        "total_active": workload["total_active"],
                        "sla_overdue": workload["sla_overdue"],
                    }
                )

            # SLA 초과가 없는 담당자 중에서 업무량이 가장 적은 담당자 선택
            available_assignees = [
                a for a in assignee_workloads if a["sla_overdue"] == 0
            ]

            if available_assignees:
                # 업무량이 가장 적은 담당자 선택
                selected = min(available_assignees, key=lambda x: x["total_active"])
                return selected["assignee_id"]
            else:
                # 모든 담당자가 SLA 초과인 경우, 업무량이 가장 적은 담당자 선택
                selected = min(assignee_workloads, key=lambda x: x["total_active"])
                return selected["assignee_id"]

        except Exception as e:
            log_error(e, None, "Auto assign dispute failed")
            return None

    @staticmethod
    def reassign_dispute(dispute_id, new_assignee_id, reason=""):
        """담당자 재배정"""
        try:
            dispute = AttendanceReport.query.get(dispute_id)
            if not dispute:
                return False, "신고/이의제기를 찾을 수 없습니다."

            new_assignee = User.query.get(new_assignee_id)
            if not new_assignee:
                return False, "새 담당자를 찾을 수 없습니다."

            old_assignee_id = dispute.assignee_id
            dispute.assignee_id = new_assignee_id
            dispute.sla_due = datetime.utcnow() + timedelta(days=3)  # SLA 재설정
            dispute.updated_at = datetime.utcnow()

            db.session.commit()

            # 새 담당자에게 알림
            send_notification_enhanced(
                user_id=new_assignee_id,
                content=f"신고/이의제기 담당자로 배정되었습니다. (신고자: {dispute.user.name or dispute.user.username})",
                category="신고/이의제기",
                link=f"/admin_dashboard/my_reports",
            )

            # 기존 담당자에게 알림 (변경된 경우)
            if old_assignee_id and old_assignee_id != new_assignee_id:
                send_notification_enhanced(
                    user_id=old_assignee_id,
                    content=f"담당 신고/이의제기가 다른 담당자로 이관되었습니다.",
                    category="신고/이의제기",
                )

            log_action(
                user_id=new_assignee_id,
                action="DISPUTE_REASSIGNED",
                message=f"신고/이의제기 {dispute_id} 재배정됨 (사유: {reason})",
            )

            return True, "담당자가 성공적으로 변경되었습니다."

        except Exception as e:
            log_error(e, None)
            return False, "담당자 변경 중 오류가 발생했습니다."

    @staticmethod
    def check_sla_overdue():
        """SLA 기한 초과 확인 및 알림"""
        try:
            now = datetime.utcnow()
            overdue_disputes = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due < now,
                    AttendanceReport.assignee_id.isnot(None),
                )
            ).all()

            for dispute in overdue_disputes:
                # 담당자에게 SLA 초과 알림
                send_notification_enhanced(
                    user_id=dispute.assignee_id,
                    content=f"⚠️ SLA 초과: 신고/이의제기 처리 기한이 초과되었습니다! (신고자: {dispute.user.name or dispute.user.username})",
                    category="SLA경고",
                )

                # 관리자에게도 알림
                admin_users = User.query.filter(User.role == "admin").all()
                for admin in admin_users:
                    if admin.id != dispute.assignee_id:  # 담당자 본인 제외
                        send_notification_enhanced(
                            user_id=admin.id,
                            content=f"SLA 초과 알림: {dispute.assignee.name or dispute.assignee.username} 담당 신고/이의제기 기한 초과",
                            category="SLA경고",
                        )

                log_action(
                    user_id=dispute.assignee_id,
                    action="SLA_OVERDUE",
                    message=f"신고/이의제기 {dispute.id} SLA 초과",
                )

            return len(overdue_disputes)

        except Exception as e:
            log_error(e, None)
            return 0

    @staticmethod
    def get_assignee_workload(assignee_id):
        """담당자별 업무량 조회"""
        try:
            # 대기중인 건수
            pending_count = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.assignee_id == assignee_id,
                    AttendanceReport.status == "pending",
                )
            ).count()

            # 처리중인 건수
            processing_count = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.assignee_id == assignee_id,
                    AttendanceReport.status == "processing",
                )
            ).count()

            # SLA 임박 건수 (24시간 이내)
            sla_urgent = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.assignee_id == assignee_id,
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due <= datetime.utcnow() + timedelta(hours=24),
                    AttendanceReport.sla_due > datetime.utcnow(),
                )
            ).count()

            # SLA 초과 건수
            sla_overdue = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.assignee_id == assignee_id,
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due < datetime.utcnow(),
                )
            ).count()

            return {
                "pending": pending_count,
                "processing": processing_count,
                "sla_urgent": sla_urgent,
                "sla_overdue": sla_overdue,
                "total_active": pending_count + processing_count,
            }

        except Exception as e:
            log_error(e, None)
            return {
                "pending": 0,
                "processing": 0,
                "sla_urgent": 0,
                "sla_overdue": 0,
                "total_active": 0,
            }

    @staticmethod
    def get_assignee_stats():
        """전체 담당자 통계"""
        try:
            # 담당자별 통계
            assignee_stats = (
                db.session.query(
                    User.name,
                    User.id,
                    func.count(AttendanceReport.id).label("total"),
                    func.sum(
                        func.case([(AttendanceReport.status == "pending", 1)], else_=0)
                    ).label("pending"),
                    func.sum(
                        func.case(
                            [(AttendanceReport.status == "processing", 1)], else_=0
                        )
                    ).label("processing"),
                    func.sum(
                        func.case([(AttendanceReport.status == "resolved", 1)], else_=0)
                    ).label("resolved"),
                )
                .join(AttendanceReport, User.id == AttendanceReport.assignee_id)
                .group_by(User.id, User.name)
                .order_by(func.count(AttendanceReport.id).desc())
                .all()
            )

            # SLA 통계
            sla_overdue_count = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due < datetime.utcnow(),
                )
            ).count()

            sla_urgent_count = AttendanceReport.query.filter(
                and_(
                    AttendanceReport.status.in_(["pending", "processing"]),
                    AttendanceReport.sla_due <= datetime.utcnow() + timedelta(hours=24),
                    AttendanceReport.sla_due > datetime.utcnow(),
                )
            ).count()

            return {
                "assignee_stats": assignee_stats,
                "sla_overdue": sla_overdue_count,
                "sla_urgent": sla_urgent_count,
            }

        except Exception as e:
            log_error(e, None)
            return {"assignee_stats": [], "sla_overdue": 0, "sla_urgent": 0}


def assign_dispute(dispute_id, assignee_id=None, reason=None):
    """신고/이의제기 담당자 배정"""
    try:
        dispute = AttendanceReport.query.get(dispute_id)
        if not dispute:
            return False, "신고/이의제기를 찾을 수 없습니다."

        # 담당자 자동 배정 (지정되지 않은 경우)
        # assignee_id = auto_assign_dispute(dispute)  # 정의되지 않은 함수, 주석 처리

        # 기존 담당자와 다른 경우에만 업데이트
        if dispute.assignee_id != assignee_id:
            old_assignee_id = dispute.assignee_id
            dispute.assignee_id = assignee_id
            dispute.sla_due = datetime.utcnow() + timedelta(days=3)  # 3일 SLA
            dispute.updated_at = datetime.utcnow()

            db.session.commit()

            # 새 담당자에게 알림
            if assignee_id:
                send_notification_enhanced(
                    user_id=assignee_id,
                    content=f"신고/이의제기 담당자로 배정되었습니다. (신고 #{dispute.id})",
                    category="담당자 배정",
                    link=f"/admin_dashboard/my_reports",
                )

                # 이메일 알림 발송
                try:
                    email_service.send_dispute_notification(dispute.id, "assigned")
                except Exception as e:
                    log_error(
                        e, None, f"Email notification failed for dispute {dispute.id}"
                    )

            # 기존 담당자에게 배정 해제 알림
            if old_assignee_id and old_assignee_id != assignee_id:
                send_notification_enhanced(
                    user_id=old_assignee_id,
                    content=f"신고/이의제기 담당자 배정이 해제되었습니다. (신고 #{dispute.id})",
                    category="담당자 배정",
                    link=f"/admin_dashboard/my_reports",
                )

            log_action(
                user_id=assignee_id,
                action="담당자 배정",
                message=f"신고 #{dispute.id} -> 담당자 {assignee_id}",
            )

            return True, "담당자 배정이 완료되었습니다."
        else:
            return True, "이미 배정된 담당자입니다."

    except Exception as e:
        log_error(e, None, f"Assignee assignment failed for dispute {dispute_id}")
        return False, f"담당자 배정 실패: {str(e)}"


def assign_cleaning_tasks():
    """청소 업무 자동 배정"""
    try:
        today = datetime.now().date()
        
        # 오늘 청소 업무가 배정되지 않은 직원들 찾기
        available_staff = (
            db.session.query(User)
            .filter(
                and_(
                    User.role == "staff",
                    User.status == "approved",
                    ~db.session.query(Attendance).filter(
                        and_(
                            Attendance.user_id == User.id,
                            Attendance.date == today,
                            Attendance.cleaning_assigned == True
                        )
                    ).exists()
                )
            )
            .all()
        )

        # 청소 업무 배정
        cleaning_tasks = [
            "주방 청소",
            "매장 청소", 
            "화장실 청소",
            "테이블 정리"
        ]

        for i, user in enumerate(available_staff):
            if i < len(cleaning_tasks):
                # 근태 기록에 청소 업무 추가
                attendance = Attendance.query.filter_by(
                    user_id=user.id, date=today
                ).first()
                
                if attendance:
                    attendance.cleaning_assigned = True
                    attendance.cleaning_task = cleaning_tasks[i]
                    
                    log_action(
                        user.id,
                        "CLEANING_ASSIGNED",
                        f"청소 업무 배정: {cleaning_tasks[i]}"
                    )

        db.session.commit()
        logger.info(f"청소 업무 배정 완료: {len(available_staff)}명")

    except Exception as e:
        logger.error(f"청소 업무 배정 실패: {e}")
        db.session.rollback()


def assign_inventory_check():
    """재고 점검 업무 자동 배정"""
    try:
        today = datetime.now().date()
        
        # 매니저 중 오늘 재고 점검이 배정되지 않은 사람 찾기
        available_managers = (
            db.session.query(User)
            .filter(
                and_(
                    User.role == "manager",
                    User.status == "approved",
                    ~db.session.query(Attendance).filter(
                        and_(
                            Attendance.user_id == User.id,
                            Attendance.date == today,
                            Attendance.inventory_check_assigned == True
                        )
                    ).exists()
                )
            )
            .all()
        )

        # 재고 점검 업무 배정
        for user in available_managers:
            attendance = Attendance.query.filter_by(
                user_id=user.id, date=today
            ).first()
            
            if attendance:
                attendance.inventory_check_assigned = True
                attendance.inventory_check_task = "전체 재고 점검"
                
                log_action(
                    user.id,
                    "INVENTORY_CHECK_ASSIGNED",
                    "재고 점검 업무 배정"
                )

        db.session.commit()
        logger.info(f"재고 점검 업무 배정 완료: {len(available_managers)}명")

    except Exception as e:
        logger.error(f"재고 점검 업무 배정 실패: {e}")
        db.session.rollback()


def assign_quality_control():
    """품질 관리 업무 자동 배정"""
    try:
        today = datetime.now().date()
        
        # 품질 관리 담당자 찾기
        quality_staff = (
            db.session.query(User)
            .filter(
                and_(
                    User.role.in_(["manager", "staff"]),
                    User.status == "approved",
                    ~db.session.query(Attendance).filter(
                        and_(
                            Attendance.user_id == User.id,
                            Attendance.date == today,
                            Attendance.quality_check_assigned == True
                        )
                    ).exists()
                )
            )
            .limit(2)  # 최대 2명
            .all()
        )

        # 품질 관리 업무 배정
        quality_tasks = ["음식 품질 점검", "서비스 품질 점검"]
        
        for i, user in enumerate(quality_staff):
            if i < len(quality_tasks):
                attendance = Attendance.query.filter_by(
                    user_id=user.id, date=today
                ).first()
                
                if attendance:
                    attendance.quality_check_assigned = True
                    attendance.quality_check_task = quality_tasks[i]
                    
                    log_action(
                        user.id,
                        "QUALITY_CHECK_ASSIGNED",
                        f"품질 관리 업무 배정: {quality_tasks[i]}"
                    )

        db.session.commit()
        logger.info(f"품질 관리 업무 배정 완료: {len(quality_staff)}명")

    except Exception as e:
        logger.error(f"품질 관리 업무 배정 실패: {e}")
        db.session.rollback()


# 전역 인스턴스
assignee_manager = AssigneeManager()
