from app_core import app, db, User, Schedule

def test_database():
    with app.app_context():
        print("=== 데이터베이스 상태 확인 ===")
        print(f"관리자 계정 수: {User.query.filter_by(role='admin').count()}")
        print(f"전체 사용자 수: {User.query.count()}")
        print(f"스케줄 데이터 수: {Schedule.query.count()}")
        
        # 관리자 계정 정보
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"관리자 계정: {admin.username}")
        
        # 스케줄 테이블 구조 확인
        try:
            schedules = Schedule.query.limit(1).all()
            print("스케줄 테이블 접근 성공")
        except Exception as e:
            print(f"스케줄 테이블 오류: {e}")

if __name__ == "__main__":
    test_database() 