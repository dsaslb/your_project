from app import app
from models import db, User
from werkzeug.security import generate_password_hash

app.app_context().push()

# 기존 admin 계정 삭제
existing_admin = User.query.filter_by(username='admin').first()
if existing_admin:
    db.session.delete(existing_admin)
    db.session.commit()
    print('기존 admin 계정 삭제 완료')

# 새로운 admin 계정 생성
new_admin = User(
    username='admin',
    email='admin@example.com',
    password_hash=generate_password_hash('admin123'),
    role='admin',
    status='approved'
)
db.session.add(new_admin)
db.session.commit()

print('새로운 admin 계정 생성 완료: admin/admin123')

# 비밀번호 확인
user = User.query.filter_by(username='admin').first()
print('비밀번호 확인 admin123:', user.check_password('admin123')) 