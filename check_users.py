from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    print(f"총 사용자 수: {len(users)}")
    for user in users:
        print(f"- {user.username} ({user.role})") 