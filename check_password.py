from app import app
from models_main import db, User

app.app_context().push()
user = User.query.filter_by(username="admin").first()

if user:
    print("User:", user.username)
    print("Password hash:", user.password_hash)
    print("Check admin123:", user.check_password("admin123"))
    print("Check admin:", user.check_password("admin"))
    print("Check password:", user.check_password("password"))
    print("Check 123456:", user.check_password("123456"))
else:
    print("Admin user not found")
