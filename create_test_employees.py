from app import app, db
from models import User

def create_test_employees():
    with app.app_context():
        # 기존 직원 확인
        existing_employees = User.query.filter_by(role='employee').all()
        if existing_employees:
            print(f"이미 {len(existing_employees)}명의 직원이 있습니다.")
            return
        
        # 테스트 직원 생성
        test_employees = [
            {"username": "employee1", "password": "testuser123", "name": "김직원1", "role": "employee"},
            {"username": "employee2", "password": "testuser234", "name": "김직원2", "role": "employee"},
            {"username": "employee3", "password": "testuser345", "name": "김직원3", "role": "employee"},
            {"username": "manager1", "password": "manager123", "name": "박매니저", "role": "manager"},
        ]
        
        for emp in test_employees:
            user = User(
                username=emp["username"],
                name=emp["name"],
                role=emp["role"],
                status="approved"
            )
            user.set_password(emp["password"])
            db.session.add(user)
        
        db.session.commit()
        print(f"{len(test_employees)}명의 테스트 사용자가 생성되었습니다.")

if __name__ == "__main__":
    create_test_employees() 