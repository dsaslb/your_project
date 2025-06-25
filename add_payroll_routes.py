#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def add_payroll_routes():
    """app.py에 급여명세서 PDF 라우트와 교대 신청 관련 라우트들을 추가합니다."""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 파일 끝에 새로운 라우트들 추가
    new_routes = '''

# --- Payroll Routes ---
@app.route('/payroll_pdf/<int:year>/<int:month>')
@login_required
def payroll_pdf(year, month):
    from utils.payroll import generate_payroll_pdf
    import os
    user = User.query.get(session['user_id'])
    records = Attendance.query.filter(
        Attendance.user_id == user.id,
        db.extract('year', Attendance.clock_in) == year,
        db.extract('month', Attendance.clock_in) == month,
        Attendance.clock_out.isnot(None)
    ).all()
    work_days = len(records)
    total_seconds = sum([(r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out])
    total_hours = int(total_seconds // 3600)
    wage = total_hours * 12000
    filename = f"payroll_{user.username}_{year}_{month}.pdf"
    filepath = os.path.join('static', filename)
    generate_payroll_pdf(filepath, user, month, year, work_days, total_hours, wage)
    return redirect(url_for('static', filename=filename))

# --- Shift Request Routes ---
@app.route('/shift_request', methods=['GET', 'POST'])
@login_required
def shift_request():
    from datetime import datetime
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        desired_date = request.form['desired_date']
        reason = request.form['reason']
        new_req = ShiftRequest(
            user_id=user.id,
            request_date=datetime.utcnow().date(),
            desired_date=desired_date,
            reason=reason,
            status='pending'
        )
        db.session.add(new_req)
        db.session.commit()
        flash("교대/근무 변경 신청이 접수되었습니다!")
        return redirect(url_for('shift_request'))
    requests = ShiftRequest.query.filter_by(user_id=user.id).order_by(ShiftRequest.created_at.desc()).all()
    return render_template('shift_request.html', requests=requests)

@app.route('/admin/shift_requests')
@login_required
def admin_shift_requests():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    requests = ShiftRequest.query.order_by(ShiftRequest.created_at.desc()).all()
    return render_template('admin/shift_requests.html', requests=requests)

@app.route('/admin/shift_request_action/<int:request_id>/<action>')
@login_required
def shift_request_action(request_id, action):
    if not current_user.is_admin():
        return redirect(url_for('index'))
    req = ShiftRequest.query.get_or_404(request_id)
    if action == 'approve':
        req.status = 'approved'
        # 알림 전송
        send_notification_enhanced(req.user, f"{req.desired_date} 근무 변경이 승인되었습니다.", category='근무')
    elif action == 'reject':
        req.status = 'rejected'
        send_notification_enhanced(req.user, f"{req.desired_date} 근무 변경이 거절되었습니다.", category='근무')
    db.session.commit()
    flash("처리가 완료되었습니다.")
    return redirect(url_for('admin_shift_requests'))

# --- Calendar Route ---
@app.route('/calendar')
@login_required
def calendar():
    user = User.query.get(session['user_id'])
    # 출근/근무 변경 등 일정을 FullCalendar로 변환
    records = Attendance.query.filter_by(user_id=user.id).all()
    shift_reqs = ShiftRequest.query.filter_by(user_id=user.id, status='approved').all()
    events = []
    for rec in records:
        events.append({
            "title": "출근",
            "start": rec.clock_in.strftime('%Y-%m-%d'),
            "color": "#00aaff"
        })
    for req in shift_reqs:
        events.append({
            "title": "근무변경(승인)",
            "start": req.desired_date.strftime('%Y-%m-%d'),
            "color": "#ffbb00"
        })
    return render_template('calendar.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    # 파일 끝의 if __name__ == '__main__' 부분을 찾아서 교체
    if 'if __name__ == \'__main__\':' in content:
        # 기존 main 부분 제거하고 새로운 라우트들 추가
        content = content.replace(
            'if __name__ == \'__main__\':\n    app.run(debug=True)',
            new_routes
        )
    else:
        # 파일 끝에 추가
        content += new_routes
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("급여명세서 PDF 라우트와 교대 신청 라우트 추가 완료!")

if __name__ == '__main__':
    add_payroll_routes() 