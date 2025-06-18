from restaurant_project.models import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_sample_data():
    """샘플 데이터 생성"""
    
    # 최고관리자 생성
    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        role='admin',
        status='approved',
        phone='010-1234-5678'
    )
    db.session.add(admin)
    db.session.commit()
    
    # 매장관리자 생성
    manager1 = User(
        username='manager1',
        password=generate_password_hash('manager123'),
        role='manager',
        status='approved',
        parent_id=admin.id,
        phone='010-2345-6789'
    )
    manager2 = User(
        username='manager2',
        password=generate_password_hash('manager123'),
        role='manager',
        status='pending',
        parent_id=admin.id,
        phone='010-3456-7890'
    )
    db.session.add_all([manager1, manager2])
    db.session.commit()
    
    # 직원 생성
    employee1 = User(
        username='employee1',
        password=generate_password_hash('employee123'),
        role='employee',
        status='approved',
        parent_id=manager1.id,
        phone='010-4567-8901'
    )
    employee2 = User(
        username='employee2',
        password=generate_password_hash('employee123'),
        role='employee',
        status='pending',
        parent_id=manager1.id,
        phone='010-5678-9012'
    )
    employee3 = User(
        username='employee3',
        password=generate_password_hash('employee123'),
        role='employee',
        status='rejected',
        parent_id=manager1.id,
        phone='010-6789-0123'
    )
    db.session.add_all([employee1, employee2, employee3])
    db.session.commit()
    
    print("샘플 데이터가 생성되었습니다.")
    print("최고관리자: admin / admin123")
    print("매장관리자: manager1 / manager123")
    print("직원: employee1 / employee123")

def create_sample_users():
    users = [
        User(username='admin01', password='adminpass', role='admin', status='approved'),
        User(username='manager01', password='managerpass', role='manager', status='approved'),
        User(username='employee01', password='employeepass', role='employee', status='approved'),
    ]
    db.session.add_all(users)
    db.session.commit()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        create_sample_data() 