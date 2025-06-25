"""
알림 자동화 라우트
- 승인/거절 자동 알림
- AI 사유 분석
- 모바일 알림 API
- 알림센터 대시보드
- 팀별/역할별 알림
- AI 기반 우선순위
"""

from flask import Blueprint, jsonify, request, render_template, Response, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
import time

from models import db, User, Notification, Attendance, ReasonTemplate, ReasonEditLog

notification_automation_bp = Blueprint('notification_automation', __name__)

def send_automated_notification(user_id, content, category='공지', link=None):
    """자동화된 알림 발송 함수"""
    try:
        notification = Notification(
            user_id=user_id,
            content=content,
            category=category,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        print(f"알림 발송 오류: {e}")
        return False

def send_notification(user_id=None, content='', category='공지', link=None,
                     recipient_role=None, recipient_team=None, priority='일반'):
    """개선된 알림 발송 함수 - 팀별/역할별 지원"""
    try:
        # AI 우선순위 분석
        ai_priority = ai_classify_notification(content)
        
        if user_id:
            # 개별 사용자에게 발송
            notification = Notification(
                user_id=user_id,
                content=content,
                category=category,
                link=link,
                priority=priority,
                ai_priority=ai_priority
            )
            db.session.add(notification)
        
        if recipient_role or recipient_team:
            # 역할별/팀별 발송
            q = User.query.filter_by(status='approved')
            if recipient_role:
                q = q.filter_by(role=recipient_role)
            if recipient_team:
                q = q.filter_by(team=recipient_team)
            
            for user in q.all():
                notification = Notification(
                    user_id=user.id,
                    content=content,
                    category=category,
                    link=link,
                    recipient_role=recipient_role,
                    recipient_team=recipient_team,
                    priority=priority,
                    ai_priority=ai_priority
                )
                db.session.add(notification)
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"알림 발송 오류: {e}")
        return False

def ai_classify_notification(content):
    """AI 기반 알림 분류/우선순위 추천"""
    content_lower = content.lower()
    
    # 긴급 키워드
    if any(keyword in content_lower for keyword in ['긴급', '사고', '화재', '응급', '즉시']):
        return '긴급'
    
    # 중요 키워드
    if any(keyword in content_lower for keyword in ['승인', '거절', '경고', '지각', '해고', '징계']):
        return '중요'
    
    # 일반 키워드
    if any(keyword in content_lower for keyword in ['공지', '안내', '알림', '일정']):
        return '일반'
    
    return '일반'

def send_mobile_push(user, message):
    """모바일 푸시 알림 (샘플)"""
    # 추후 FCM/APNS 연동
    print(f"[푸시알림] {user.username}: {message}")

def send_notification_with_push(user_id, content, **kwargs):
    """푸시 알림과 함께 알림 발송"""
    user = User.query.get(user_id)
    success = send_notification(user_id=user_id, content=content, **kwargs)
    if success and user:
        send_mobile_push(user, content)
    return success

def ai_reason_analyze(user_id):
    """AI 사유 분석 및 자동 경고"""
    try:
        # 최근 30일 근태 기록 조회
        recent = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.clock_in >= (datetime.now() - timedelta(days=30))
        ).all()
        
        # 사유별 카운트
        reason_counts = {}
        for record in recent:
            if record.reason:
                reason = record.reason.strip()
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        warnings = []
        recommendations = []
        
        # 지각 관련 경고
        late_count = sum(count for reason, count in reason_counts.items() if '지각' in reason)
        if late_count >= 5:
            warnings.append(f"지각 {late_count}회 - 경고 대상")
            recommendations.append("출근 시간을 앞당겨보세요")
        elif late_count >= 3:
            warnings.append(f"지각 {late_count}회 - 주의 필요")
        
        # 병가 관련 경고
        sick_count = sum(count for reason, count in reason_counts.items() if '병가' in reason or '아픔' in reason)
        if sick_count >= 3:
            warnings.append(f"병가 {sick_count}회 - 복지 상담 권장")
            recommendations.append("건강 검진을 받아보세요")
        
        return {
            'warnings': warnings,
            'recommendations': recommendations,
            'total_records': len(recent),
            'reason_counts': reason_counts
        }
    except Exception as e:
        print(f"AI 분석 오류: {e}")
        return {
            'warnings': [],
            'recommendations': [],
            'total_records': 0,
            'reason_counts': {}
        }

# 알림센터 대시보드
@notification_automation_bp.route('/notifications/dashboard')
@login_required
def notifications_dashboard():
    """알림센터 대시보드 - 필터/검색/상태 집계"""
    user_id = session.get('user_id')
    role = session.get('role')
    
    # 알림 필터
    q = Notification.query
    if role != 'admin':
        q = q.filter_by(user_id=user_id)
    
    # 카테고리 필터
    category = request.args.get('category')
    if category:
        q = q.filter_by(category=category)
    
    # 읽음 상태 필터
    is_read = request.args.get('is_read')
    if is_read in ['0', '1']:
        q = q.filter_by(is_read=bool(int(is_read)))
    
    # 우선순위 필터
    priority = request.args.get('priority')
    if priority:
        q = q.filter_by(priority=priority)
    
    # 키워드 검색
    keyword = request.args.get('q')
    if keyword:
        q = q.filter(Notification.content.contains(keyword))
    
    # 알림 목록 조회
    notifications = q.order_by(Notification.created_at.desc()).limit(100).all()
    
    # 상태 집계
    total = q.count()
    unread = q.filter_by(is_read=False).count()
    
    # 카테고리별 통계
    category_stats = db.session.query(
        Notification.category,
        func.count().label('count')
    ).filter_by(user_id=user_id).group_by(Notification.category).all()
    
    # 우선순위별 통계
    priority_stats = db.session.query(
        Notification.priority,
        func.count().label('count')
    ).filter_by(user_id=user_id).group_by(Notification.priority).all()
    
    return render_template('notifications/dashboard.html',
                         notifications=notifications,
                         total=total,
                         unread=unread,
                         category_stats=category_stats,
                         priority_stats=priority_stats)

# 알림 읽음 처리
@notification_automation_bp.route('/notifications/mark_read', methods=['POST'])
@login_required
def mark_notification_read():
    """알림 읽음 처리"""
    notification_id = request.json.get('notification_id')
    
    if not notification_id:
        return jsonify({'error': 'notification_id required'}), 400
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Notification not found'}), 404

# 알림 통계 차트
@notification_automation_bp.route('/notifications/stats')
@login_required
def notifications_stats():
    """알림 통계 차트 - 일별/카테고리별"""
    user_id = session.get('user_id')
    role = session.get('role')
    
    # 쿼리 구성
    q = Notification.query
    if role != 'admin':
        q = q.filter_by(user_id=user_id)
    
    # 일별 통계 (최근 30일)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    daily_stats = db.session.query(
        func.date(Notification.created_at).label('date'),
        func.count().label('count')
    ).filter(
        Notification.created_at >= start_date
    )
    
    if role != 'admin':
        daily_stats = daily_stats.filter_by(user_id=user_id)
    
    daily_stats = daily_stats.group_by(
        func.date(Notification.created_at)
    ).order_by('date').all()
    
    # 카테고리별 통계
    category_stats = db.session.query(
        Notification.category,
        func.count().label('count')
    )
    
    if role != 'admin':
        category_stats = category_stats.filter_by(user_id=user_id)
    
    category_stats = category_stats.group_by(
        Notification.category
    ).all()
    
    # 우선순위별 통계
    priority_stats = db.session.query(
        Notification.priority,
        func.count().label('count')
    )
    
    if role != 'admin':
        priority_stats = priority_stats.filter_by(user_id=user_id)
    
    priority_stats = priority_stats.group_by(
        Notification.priority
    ).all()
    
    return render_template('notifications/stats.html',
                         daily_stats=daily_stats,
                         category_stats=category_stats,
                         priority_stats=priority_stats,
                         days=days)

# 팀별/역할별 알림 발송
@notification_automation_bp.route('/notifications/send_bulk', methods=['POST'])
@login_required
def send_bulk_notification():
    """팀별/역할별 알림 발송"""
    if not current_user.is_admin():
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    data = request.json
    content = data.get('content')
    category = data.get('category', '공지')
    recipient_role = data.get('recipient_role')
    recipient_team = data.get('recipient_team')
    priority = data.get('priority', '일반')
    send_push = data.get('send_push', False)
    
    if not content:
        return jsonify({'error': 'content required'}), 400
    
    if not recipient_role and not recipient_team:
        return jsonify({'error': 'recipient_role or recipient_team required'}), 400
    
    success = send_notification(
        content=content,
        category=category,
        recipient_role=recipient_role,
        recipient_team=recipient_team,
        priority=priority
    )
    
    if success and send_push:
        # 푸시 알림 발송
        users = User.query.filter_by(status='approved')
        if recipient_role:
            users = users.filter_by(role=recipient_role)
        if recipient_team:
            users = users.filter_by(team=recipient_team)
        
        for user in users.all():
            send_mobile_push(user, content)
    
    return jsonify({'success': success})

# AI 사유 분석 경고 페이지
@notification_automation_bp.route('/admin/ai_reason_warnings')
@login_required
def admin_ai_reason_warnings():
    """AI 사유 분석 경고 페이지"""
    if not current_user.is_admin():
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    users = User.query.filter_by(status='approved').all()
    results = []
    
    for user in users:
        analysis = ai_reason_analyze(user.id)
        if analysis['warnings']:  # 경고가 있는 경우만
            results.append({
                "user": user,
                "analysis": analysis
            })
    
    # 전체 통계
    total_warnings = sum(len(result['analysis']['warnings']) for result in results)
    total_users_with_warnings = len(results)
    
    return render_template('admin/ai_reason_warnings.html', 
                         results=results,
                         total_warnings=total_warnings,
                         total_users_with_warnings=total_users_with_warnings)

# 사유 변경 이력 차트
@notification_automation_bp.route('/admin/reason_edit_log/chart')
@login_required
def reason_edit_log_chart():
    """사유 변경 이력 차트"""
    if not current_user.is_admin():
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    # 일자별 변경 건수
    daily_data = db.session.query(
        func.date(ReasonEditLog.edited_at).label('date'),
        func.count().label('count')
    ).filter(
        ReasonEditLog.edited_at >= start_date
    ).group_by(
        func.date(ReasonEditLog.edited_at)
    ).order_by('date').all()
    
    # 차트 데이터 준비
    labels = [d.date.strftime('%m-%d') for d in daily_data]
    counts = [d.count for d in daily_data]
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'daily_labels': labels,
            'daily_counts': counts
        })
    
    return render_template('admin/reason_edit_log_chart.html',
                         labels=labels,
                         counts=counts,
                         days=days)

# 모바일 알림 API
@notification_automation_bp.route('/api/mobile/notifications')
def api_mobile_notifications():
    """모바일 알림 API"""
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    category = request.args.get('category')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    # 쿼리 구성
    q = Notification.query.filter_by(user_id=user_id)
    
    if category:
        q = q.filter_by(category=category)
    
    notifications = q.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return jsonify([{
        "id": n.id,
        "content": n.content,
        "category": n.category,
        "created_at": n.created_at.isoformat(),
        "link": n.link,
        "is_read": n.is_read,
        "priority": n.priority
    } for n in notifications])

@notification_automation_bp.route('/api/mobile/notifications/mark_read', methods=['POST'])
def api_mobile_mark_notification_read():
    """모바일 알림 읽음 처리 API"""
    user_id = request.json.get('user_id')
    notification_id = request.json.get('notification_id')
    
    if not user_id or not notification_id:
        return jsonify({'error': 'user_id and notification_id required'}), 400
    
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=user_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Notification not found'}), 404

@notification_automation_bp.route('/api/mobile/notifications/unread_count')
def api_mobile_unread_count():
    """모바일 읽지 않은 알림 개수 API"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    count = Notification.query.filter_by(
        user_id=user_id, 
        is_read=False
    ).count()
    
    return jsonify({'unread_count': count})

# 실시간 알림 스트림
@notification_automation_bp.route('/api/notifications/stream')
@login_required
def notifications_stream():
    """실시간 알림 스트림 (Server-Sent Events)"""
    def generate():
        while True:
            try:
                # 읽지 않은 알림 개수 확인
                unread_count = Notification.query.filter_by(
                    user_id=current_user.id, 
                    is_read=False
                ).count()
                
                yield f"data: {unread_count}\n\n"
                time.sleep(30)  # 30초마다 업데이트
            except Exception as e:
                print(f"알림 스트림 오류: {e}")
                break
    
    return Response(generate(), mimetype='text/plain')

# 알림 발송 API
@notification_automation_bp.route('/api/notifications/send', methods=['POST'])
@login_required
def api_send_notification():
    """알림 발송 API"""
    if not current_user.is_admin():
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content')
    category = data.get('category', '공지')
    
    if not user_id or not content:
        return jsonify({'error': 'user_id and content required'}), 400
    
    success = send_automated_notification(user_id, content, category)
    return jsonify({'success': success})

# 사용자 정보 API
@notification_automation_bp.route('/api/user/<int:user_id>')
@login_required
def api_user_info(user_id):
    """사용자 정보 API"""
    if not current_user.is_admin():
        return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'branch': user.branch.name if user.branch else None
    }) 