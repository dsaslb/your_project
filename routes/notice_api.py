from datetime import datetime
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, render_template, request
form = None  # pyright: ignore

notice_api_bp = Blueprint('notice_api', __name__)


@notice_api_bp.route('/notice')
@login_required
def notice():
    """알림/공지사항 메인 페이지"""
    return render_template('notice.html', user=current_user)


@notice_api_bp.route('/api/notifications')
@login_required
def get_notifications():
    """알림 목록 조회 API"""
    # 더미 알림 데이터
    notifications = [
        {
            "id": 1,
            "title": "새로운 주문 등록",
            "content": "테이블 5번에서 새로운 주문이 등록되었습니다.",
            "category": "주문",
            "priority": "일반",
            "is_read": False,
            "created_at": "2024-01-15T14:30:00Z",
            "related_url": "/orders"
        },
        {
            "id": 2,
            "title": "재고 부족 알림",
            "content": "토마토 소스 재고가 부족합니다. 발주가 필요합니다.",
            "category": "재고",
            "priority": "중요",
            "is_read": False,
            "created_at": "2024-01-15T13:45:00Z",
            "related_url": "/inventory"
        },
        {
            "id": 3,
            "title": "직원 출근",
            "content": "김철수 직원이 출근했습니다.",
            "category": "직원",
            "priority": "일반",
            "is_read": True,
            "created_at": "2024-01-15T09:00:00Z",
            "related_url": "/staff"
        },
        {
            "id": 4,
            "title": "시스템 점검 예정",
            "content": "오늘 밤 12시부터 2시간 동안 시스템 점검이 예정되어 있습니다.",
            "category": "시스템",
            "priority": "긴급",
            "is_read": False,
            "created_at": "2024-01-15T10:15:00Z",
            "related_url": "/dashboard"
        }
    ]

    return jsonify({"success": True, "data": notifications})


@notice_api_bp.route('/api/notices')
@login_required
def get_notices():
    """공지사항 목록 조회 API"""
    # 더미 공지사항 데이터
    notices = [
        {
            "id": 1,
            "title": "월간 직원 회의 안내",
            "content": "다음 주 월요일 오후 2시에 월간 직원 회의가 예정되어 있습니다. 모든 직원의 참석을 부탁드립니다.",
            "category": "회의",
            "author": "매니저",
            "created_at": "2024-01-15T10:00:00Z",
            "is_hidden": False
        },
        {
            "id": 2,
            "title": "메뉴 변경 안내",
            "content": "고객 피드백을 반영하여 일부 메뉴가 변경되었습니다. 새로운 메뉴 가격표를 확인해주세요.",
            "category": "메뉴",
            "author": "주방장",
            "created_at": "2024-01-14T15:30:00Z",
            "is_hidden": False
        },
        {
            "id": 3,
            "title": "청소 일정 변경",
            "content": "이번 주 청소 일정이 변경되었습니다. 새로운 일정표를 확인해주세요.",
            "category": "청소",
            "author": "관리자",
            "created_at": "2024-01-13T09:15:00Z",
            "is_hidden": False
        }
    ]

    return jsonify({"success": True, "data": notices})


@notice_api_bp.route('/api/notifications', methods=['POST'])
@login_required
def create_notification():
    """알림 생성 API"""
    data = request.get_json()

    # 더미 응답
    new_notification = {
        "id": 999,
        "title": data.get() if data else None'title', '새 알림') if data else None,
        "content": data.get() if data else None'content', '알림 내용') if data else None,
        "category": data.get() if data else None'category', '일반') if data else None,
        "priority": data.get() if data else None'priority', '일반') if data else None,
        "is_read": False,
        "created_at": datetime.now().isoformat(),
        "related_url": data.get() if data else None'related_url', '') if data else None
    }

    return jsonify({"success": True, "data": new_notification, "message": "알림이 생성되었습니다."})


@notice_api_bp.route('/api/notices', methods=['POST'])
@login_required
def create_notice():
    """공지사항 생성 API"""
    data = request.get_json()

    # 더미 응답
    new_notice = {
        "id": 999,
        "title": data.get() if data else None'title', '새 공지사항') if data else None,
        "content": data.get() if data else None'content', '공지사항 내용') if data else None,
        "category": data.get() if data else None'category', '일반') if data else None,
        "author": current_user.name if current_user.is_authenticated else "시스템",
        "created_at": datetime.now().isoformat(),
        "is_hidden": False
    }

    return jsonify({"success": True, "data": new_notice, "message": "공지사항이 생성되었습니다."})


@notice_api_bp.route('/api/notifications/<int:notification_id>', methods=['PUT'])
@login_required
def update_notification(notification_id):
    """알림 수정 API"""
    data = request.get_json()

    # 더미 응답
    updated_notification = {
        "id": notification_id,
        "title": data.get() if data else None'title', '수정된 알림') if data else None,
        "content": data.get() if data else None'content', '수정된 내용') if data else None,
        "category": data.get() if data else None'category', '일반') if data else None,
        "priority": data.get() if data else None'priority', '일반') if data else None,
        "is_read": data.get() if data else None'is_read', False) if data else None,
        "updated_at": datetime.now().isoformat()
    }

    return jsonify({"success": True, "data": updated_notification, "message": "알림이 수정되었습니다."})


@notice_api_bp.route('/api/notices/<int:notice_id>', methods=['PUT'])
@login_required
def update_notice(notice_id):
    """공지사항 수정 API"""
    data = request.get_json()

    # 더미 응답
    updated_notice = {
        "id": notice_id,
        "title": data.get() if data else None'title', '수정된 공지사항') if data else None,
        "content": data.get() if data else None'content', '수정된 내용') if data else None,
        "category": data.get() if data else None'category', '일반') if data else None,
        "author": data.get() if data else None'author', '수정자') if data else None,
        "updated_at": datetime.now().isoformat(),
        "is_hidden": data.get() if data else None'is_hidden', False) if data else None
    }

    return jsonify({"success": True, "data": updated_notice, "message": "공지사항이 수정되었습니다."})


@notice_api_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """알림 삭제 API"""
    return jsonify({"success": True, "message": f"알림 {notification_id}가 삭제되었습니다."})


@notice_api_bp.route('/api/notices/<int:notice_id>', methods=['DELETE'])
@login_required
def delete_notice(notice_id):
    """공지사항 삭제 API"""
    return jsonify({"success": True, "message": f"공지사항 {notice_id}가 삭제되었습니다."})


@notice_api_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리 API"""
    return jsonify({"success": True, "message": f"알림 {notification_id}가 읽음 처리되었습니다."})


@notice_api_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리 API"""
    return jsonify({"success": True, "message": "모든 알림이 읽음 처리되었습니다."})


@notice_api_bp.route('/api/notifications/<int:notification_id>')
@login_required
def get_notification_detail(notification_id):
    """알림 상세 조회 API"""
    # 더미 상세 데이터
    notification_detail = {
        "id": notification_id,
        "title": "새로운 주문 등록",
        "content": "테이블 5번에서 새로운 주문이 등록되었습니다. 주문 내용을 확인하고 처리해주세요.",
        "category": "주문",
        "priority": "일반",
        "is_read": False,
        "created_at": "2024-01-15T14:30:00Z",
        "related_url": "/orders",
        "recipient": "전체 직원",
        "sender": "시스템"
    }

    return jsonify({"success": True, "data": notification_detail})


@notice_api_bp.route('/api/notices/<int:notice_id>')
@login_required
def get_notice_detail(notice_id):
    """공지사항 상세 조회 API"""
    # 더미 상세 데이터
    notice_detail = {
        "id": notice_id,
        "title": "월간 직원 회의 안내",
        "content": "다음 주 월요일 오후 2시에 월간 직원 회의가 예정되어 있습니다. 모든 직원의 참석을 부탁드립니다. 회의 안건은 다음과 같습니다:\n\n1. 이번 달 실적 리뷰\n2. 다음 달 계획 수립\n3. 건의사항 논의\n4. 기타 안건",
        "category": "회의",
        "author": "매니저",
        "created_at": "2024-01-15T10:00:00Z",
        "is_hidden": False,
        "read_count": 15,
        "comments": []
    }

    return jsonify({"success": True, "data": notice_detail})


@notice_api_bp.route('/api/notifications/stats')
@login_required
def get_notification_stats():
    """알림 통계 API"""
    # 더미 통계 데이터
    stats = {
        "total_notifications": 45,
        "unread_notifications": 8,
        "read_notifications": 37,
        "by_category": {
            "주문": 15,
            "재고": 8,
            "직원": 12,
            "시스템": 10
        },
        "by_priority": {
            "긴급": 3,
            "중요": 12,
            "일반": 30
        }
    }

    return jsonify({"success": True, "data": stats})


@notice_api_bp.route('/api/notices/stats')
@login_required
def get_notice_stats():
    """공지사항 통계 API"""
    # 더미 통계 데이터
    stats = {
        "total_notices": 25,
        "by_category": {
            "회의": 8,
            "메뉴": 5,
            "청소": 6,
            "일반": 6
        },
        "recent_notices": [
            {
                "id": 1,
                "title": "월간 직원 회의 안내",
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "title": "메뉴 변경 안내",
                "created_at": "2024-01-14T15:30:00Z"
            }
        ]
    }

    return jsonify({"success": True, "data": stats})
