"""
Flask-SocketIO 기반 실시간 알림 시스템
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
import os

# 모델 임포트
from models_integrated import db, User, Attendance, AttendanceReport, Notification, ActionLog

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant_socketio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-SocketIO 초기화
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 데이터베이스 초기화
db.init_app(app)

# 로그인 매니저
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== 실시간 알림 시스템 =====

def send_notification(user_id, content, category="신고", link=None):
    """실시간 알림 + 이메일 발송 통합 함수"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        # 1. 데이터베이스 알림 저장
        notification = Notification(
            user_id=user_id,
            content=content,
            category=category,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        
        # 2. 실시간 SocketIO 알림
        socketio.emit('notify', {
            'user_id': user_id,
            'content': content,
            'category': category,
            'link': link or url_for('admin_reports'),
            'timestamp': datetime.utcnow().strftime('%H:%M'),
            'notification_id': notification.id
        }, room=f"user_{user_id}")
        
        # 3. 이메일 알림 (실제 구현 시)
        if user.email:
            send_email(user.email, f"[알림] {category}", content)
        
        # 4. 로그 기록
        log_action(user_id, 'NOTIFICATION_SENT', f'Notification: {content[:50]}...')
        
        return True
        
    except Exception as e:
        print(f"알림 발송 실패: {str(e)}")
        return False

def send_email(to_email, subject, body):
    """이메일 발송 함수 (실제 구현 시 SMTP 연동)"""
    print(f"[이메일] {to_email} ({subject}): {body}")
    # 실제 구현: smtplib 또는 Flask-Mail 사용

def log_action(user_id, action, details):
    """액션 로그 기록"""
    try:
        log = ActionLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"로그 기록 실패: {str(e)}")

# ===== SocketIO 이벤트 핸들러 =====

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 시"""
    print(f"클라이언트 연결: {request.sid}")
    emit('connected', {'message': '서버에 연결되었습니다.'})

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제 시"""
    print(f"클라이언트 연결 해제: {request.sid}")

@socketio.on('join')
def on_join(data):
    """사용자별 룸 입장"""
    try:
        room = data.get('room')
        if room:
            join_room(room)
            print(f"사용자 {room} 룸 입장")
            emit('joined', {'room': room, 'message': f'{room} 룸에 입장했습니다.'})
    except Exception as e:
        print(f"룸 입장 실패: {str(e)}")

@socketio.on('leave')
def on_leave(data):
    """룸 퇴장"""
    try:
        room = data.get('room')
        if room:
            leave_room(room)
            print(f"사용자 {room} 룸 퇴장")
    except Exception as e:
        print(f"룸 퇴장 실패: {str(e)}")

@socketio.on('get_notifications')
def handle_get_notifications(data):
    """알림 목록 요청"""
    try:
        user_id = data.get('user_id')
        if user_id and current_user.is_authenticated:
            notifications = Notification.query.filter_by(
                user_id=user_id, 
                is_read=False
            ).order_by(Notification.created_at.desc()).limit(10).all()
            
            emit('notifications_list', {
                'notifications': [
                    {
                        'id': n.id,
                        'content': n.content,
                        'category': n.category,
                        'link': n.link,
                        'created_at': n.created_at.strftime('%m-%d %H:%M')
                    } for n in notifications
                ]
            })
    except Exception as e:
        print(f"알림 목록 조회 실패: {str(e)}")

# ===== 라우트 =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('로그인 실패')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ===== 신고/이의제기 관리 라우트 =====

@app.route('/m/attendance/<int:att_id>/report', methods=['GET', 'POST'])
@login_required
def m_attendance_report(att_id):
    """모바일 신고/이의제기 등록"""
    try:
        att = Attendance.query.get_or_404(att_id)
        
        # 본인의 출결 기록만 신고 가능
        if att.user_id != current_user.id:
            flash('본인의 출결 기록만 신고할 수 있습니다.', 'error')
            return redirect(url_for('m_attendance_history'))
        
        if request.method == 'POST':
            reason = request.form.get('report_reason', '').strip()
            
            if not reason:
                flash('신고 사유를 입력해주세요.', 'error')
                return render_template('m_attendance_report.html', att=att)
            
            # 담당자 자동 배정 (팀장 → 관리자 순서)
            teamlead = User.query.filter_by(team=att.user.team, role='teamlead').first()
            assignee = teamlead or User.query.filter_by(role='admin').first()
            
            if not assignee:
                flash('담당자를 찾을 수 없습니다.', 'error')
                return render_template('m_attendance_report.html', att=att)
            
            # SLA 기한 설정 (3일)
            due = datetime.utcnow() + timedelta(days=3)
            
            # 신고/이의제기 생성
            new_report = AttendanceReport(
                attendance_id=att.id,
                user_id=current_user.id,
                reason=reason,
                status='pending',
                assignee_id=assignee.id,
                sla_due=due
            )
            db.session.add(new_report)
            db.session.commit()
            
            # 담당자에게 실시간 알림 발송
            send_notification(
                user_id=assignee.id,
                content=f"신규 신고/이의제기가 배정되었습니다. (신고자: {current_user.name or current_user.username})",
                category="신고",
                link=url_for('admin_reports')
            )
            
            # 로그 기록
            log_action(
                user_id=current_user.id,
                action='REPORT_CREATED',
                details=f'Created report for attendance {att_id}'
            )
            
            flash('신고/이의제기가 접수 및 담당자 배정·알림 전송됨', 'success')
            return redirect(url_for('m_attendance_history'))
        
        return render_template('m_attendance_report.html', att=att)
        
    except Exception as e:
        print(f"신고 등록 실패: {str(e)}")
        flash('신고 등록 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('m_attendance_history'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    """관리자 신고/이의제기 목록"""
    try:
        # 필터 파라미터
        status = request.args.get('status', '')
        assignee_id = request.args.get('assignee_id', '')
        
        query = AttendanceReport.query
        
        if status:
            query = query.filter(AttendanceReport.status == status)
        if assignee_id:
            query = query.filter(AttendanceReport.assignee_id == assignee_id)
        
        reports = query.order_by(AttendanceReport.created_at.desc()).all()
        
        # 담당자 목록 (재배정용)
        assignees = User.query.filter(
            User.role.in_(['admin', 'manager', 'teamlead'])
        ).order_by(User.name).all()
        
        return render_template('admin_reports.html', 
                             reports=reports, 
                             assignees=assignees)
        
    except Exception as e:
        print(f"신고 목록 조회 실패: {str(e)}")
        flash('신고 목록을 불러오는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/report/<int:report_id>/reassign', methods=['POST'])
@login_required
def report_reassign(report_id):
    """담당자 재배정"""
    try:
        if not current_user.is_manager():
            flash('권한이 없습니다.', 'error')
            return redirect(url_for('admin_reports'))
        
        report = AttendanceReport.query.get_or_404(report_id)
        new_assignee_id = int(request.form.get('assignee_id'))
        
        old_assignee_id = report.assignee_id
        report.assignee_id = new_assignee_id
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 새 담당자에게 알림
        send_notification(
            user_id=new_assignee_id,
            content=f"신고/이의제기 담당자로 위임되었습니다. (신고 #{report.id})",
            category="신고",
            link=url_for('admin_reports')
        )
        
        # 기존 담당자에게 배정 해제 알림
        if old_assignee_id and old_assignee_id != new_assignee_id:
            send_notification(
                user_id=old_assignee_id,
                content=f"신고/이의제기 담당자 배정이 해제되었습니다. (신고 #{report.id})",
                category="신고",
                link=url_for('admin_reports')
            )
        
        # 로그 기록
        log_action(
            user_id=current_user.id,
            action='REPORT_REASSIGNED',
            details=f'Reassigned report {report_id} to user {new_assignee_id}'
        )
        
        flash('담당자(위임) 변경 및 알림 완료', 'success')
        return redirect(url_for('admin_reports'))
        
    except Exception as e:
        print(f"담당자 재배정 실패: {str(e)}")
        flash('담당자 재배정 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_reports'))

@app.route('/admin/report/<int:report_id>/reply', methods=['POST'])
@login_required
def report_reply(report_id):
    """신고/이의제기 답변 처리"""
    try:
        report = AttendanceReport.query.get_or_404(report_id)
        
        # 담당자 또는 관리자만 답변 가능
        if report.assignee_id != current_user.id and not current_user.is_admin():
            flash('담당자가 아닌 신고/이의제기입니다.', 'error')
            return redirect(url_for('admin_reports'))
        
        reply = request.form.get('reply', '').strip()
        new_status = request.form.get('status', 'resolved')
        
        if not reply:
            flash('답변 내용을 입력해주세요.', 'error')
            return redirect(url_for('admin_reports'))
        
        # 상태 업데이트
        report.reply = reply
        report.status = new_status
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 신고자에게 실시간 알림
        send_notification(
            user_id=report.user_id,
            content=f"신고/이의제기에 답변이 등록되었습니다. (상태: {new_status})",
            category="신고",
            link=url_for('m_attendance_history')
        )
        
        # 로그 기록
        log_action(
            user_id=current_user.id,
            action='REPORT_REPLIED',
            details=f'Replied to report {report_id} with status {new_status}'
        )
        
        flash('답변이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('admin_reports'))
        
    except Exception as e:
        print(f"답변 처리 실패: {str(e)}")
        flash('답변 처리 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_reports'))

# ===== 차트 데이터 API =====

@app.route('/admin/report_chart_data')
@login_required
def report_chart_data():
    """신고/이의제기 차트 데이터 API"""
    try:
        # 날짜별 신고/이의제기 통계
        data = db.session.query(
            func.strftime('%Y-%m-%d', AttendanceReport.created_at).label('date'),
            func.count().label('count')
        ).group_by(
            func.strftime('%Y-%m-%d', AttendanceReport.created_at)
        ).order_by('date').all()
        
        # 상태별 통계
        status_stats = db.session.query(
            AttendanceReport.status,
            func.count().label('count')
        ).group_by(AttendanceReport.status).all()
        
        return jsonify({
            'success': True,
            'daily_data': {
                'labels': [d.date for d in data],
                'counts': [d.count for d in data]
            },
            'status_stats': {
                'labels': [s.status for s in status_stats],
                'counts': [s.count for s in status_stats]
            }
        })
        
    except Exception as e:
        print(f"차트 데이터 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== 자동 처리 규칙 =====

def auto_process_reports():
    """자동 처리 규칙 실행"""
    try:
        now = datetime.utcnow()
        
        # SLA 초과 신고/이의제기 조회
        overdue = AttendanceReport.query.filter(
            and_(
                AttendanceReport.status == 'pending',
                AttendanceReport.sla_due < now
            )
        ).all()
        
        for report in overdue:
            if report.assignee_id:
                send_notification(
                    user_id=report.assignee_id,
                    content=f"SLA 초과 미처리 신고 자동 경고! (신고 #{report.id})",
                    category="SLA"
                )
        
        print(f"SLA 초과 자동 경고 발송: {len(overdue)}건")
        
    except Exception as e:
        print(f"자동 처리 규칙 실행 실패: {str(e)}")

# ===== 앱 실행 =====

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # 개발 서버 실행 (실제 운영 시에는 gunicorn + eventlet 사용)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
