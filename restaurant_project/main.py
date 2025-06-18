from flask import Flask
from routes.auth import auth_bp
from models import db
import os

app = Flask(__name__)
app.secret_key = "your-secret-key"  # 보안을 위해 나중에 .env로 이동

# SQLite 연결
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "restaurant.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 라우트 등록
app.register_blueprint(auth_bp)

# DB 생성용
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True) 