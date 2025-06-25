#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def update_profile_route():
    """app.py의 profile 라우트를 확장합니다."""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 기존 profile 라우트를 새로운 버전으로 교체
    old_profile = '''@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)'''
    
    new_profile = '''@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    from datetime import datetime, time
    import calendar

    now = datetime.utcnow()
    monthly_stats = []
    lateness_list = []
    early_leave_list = []

    STANDARD_CLOCKIN = time(9, 0, 0)
    STANDARD_CLOCKOUT = time(18, 0, 0)

    for i in range(6):
        year = (now.year if now.month - i > 0 else now.year-1)
        month = (now.month - i) if now.month - i > 0 else 12 + (now.month - i)
        # 해당 월 출근/퇴근 기록
        records = Attendance.query.filter(
            Attendance.user_id == user.id,
            db.extract('year', Attendance.clock_in) == year,
            db.extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).all()
        work_days = len(records)
        total_seconds = sum([
            (r.clock_out - r.clock_in).total_seconds() for r in records if r.clock_out
        ])
        total_hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        wage = total_hours * 12000  # 시급 예시
        # 지각/조퇴
        lateness = sum([1 for r in records if r.clock_in and r.clock_in.time() > STANDARD_CLOCKIN])
        early_leave = sum([1 for r in records if r.clock_out and r.clock_out.time() < STANDARD_CLOCKOUT])
        lateness_list.append(lateness)
        early_leave_list.append(early_leave)
        monthly_stats.append({
            "year": year,
            "month": month,
            "work_days": work_days,
            "total_hours": total_hours,
            "minutes": minutes,
            "wage": wage,
            "lateness": lateness,
            "early_leave": early_leave,
        })
    labels = [f"{row['year']}-{row['month']:02d}" for row in monthly_stats]
    hours_list = [row['total_hours'] for row in monthly_stats]

    # 최신순 정렬
    monthly_stats = sorted(monthly_stats, key=lambda x: (x['year'], x['month']), reverse=True)

    # 최근 알림 5개
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()

    return render_template(
        'profile.html',
        user=user,
        monthly_stats=monthly_stats,
        labels=labels,
        hours_list=hours_list,
        lateness_list=lateness_list,
        early_leave_list=early_leave_list,
        notifications=notifications
    )'''
    
    content = content.replace(old_profile, new_profile)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Profile 라우트 확장 완료!")

if __name__ == '__main__':
    update_profile_route() 