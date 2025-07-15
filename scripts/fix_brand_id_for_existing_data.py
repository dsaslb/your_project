import os
import sys
from app import app, db
from models import SystemLog, Schedule, CleaningPlan, Team, PayTransfer, AIIntegration, User, Branch

# brand_id가 없는 기존 데이터 일괄 입력/이관 스크립트
# 초보자용: 반드시 백업 후 실행하세요!

def fix_brand_id():
    with app.app_context():
        # 1. SystemLog: user_id -> User.brand_id
        logs = SystemLog.query.filter(SystemLog.brand_id == None).all()
        for log in logs:
            if log.user_id:
                user = User.query.get(log.user_id)
                if user and user.brand_id:
                    log.brand_id = user.brand_id
            if not log.brand_id:
                log.brand_id = 1  # 기본값
        print(f'SystemLog: {len(logs)}건 처리')

        # 2. Schedule: user_id -> User.brand_id
        schedules = Schedule.query.filter(Schedule.brand_id == None).all()
        for s in schedules:
            if s.user_id:
                user = User.query.get(s.user_id)
                if user and user.brand_id:
                    s.brand_id = user.brand_id
            if not s.brand_id:
                s.brand_id = 1
        print(f'Schedule: {len(schedules)}건 처리')

        # 3. CleaningPlan: branch_id -> Branch.brand_id
        plans = CleaningPlan.query.filter(CleaningPlan.brand_id == None).all()
        for p in plans:
            if hasattr(p, 'branch_id') and p.branch_id:
                branch = Branch.query.get(p.branch_id)
                if branch and branch.brand_id:
                    p.brand_id = branch.brand_id
            if not p.brand_id:
                p.brand_id = 1
        print(f'CleaningPlan: {len(plans)}건 처리')

        # 4. Team: branch_id -> Branch.brand_id
        teams = Team.query.filter(Team.brand_id == None).all()
        for t in teams:
            if hasattr(t, 'branch_id') and t.branch_id:
                branch = Branch.query.get(t.branch_id)
                if branch and branch.brand_id:
                    t.brand_id = branch.brand_id
            if not t.brand_id:
                t.brand_id = 1
        print(f'Team: {len(teams)}건 처리')

        # 5. PayTransfer: user_id -> User.brand_id
        pays = PayTransfer.query.filter(PayTransfer.brand_id == None).all()
        for pay in pays:
            if pay.user_id:
                user = User.query.get(pay.user_id)
                if user and user.brand_id:
                    pay.brand_id = user.brand_id
            if not pay.brand_id:
                pay.brand_id = 1
        print(f'PayTransfer: {len(pays)}건 처리')

        # 6. AIIntegration: branch_id -> Branch.brand_id
        ais = AIIntegration.query.filter(AIIntegration.brand_id == None).all()
        for ai in ais:
            if hasattr(ai, 'branch_id') and ai.branch_id:
                branch = Branch.query.get(ai.branch_id)
                if branch and branch.brand_id:
                    ai.brand_id = branch.brand_id
            if not ai.brand_id:
                ai.brand_id = 1
        print(f'AIIntegration: {len(ais)}건 처리')

        db.session.commit()
        print('모든 테이블 brand_id 일괄 입력/이관 완료!')

if __name__ == '__main__':
    fix_brand_id() 