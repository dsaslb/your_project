from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from restaurant_project.models import db, User
from restaurant_project.routes.auth import auth_bp
from restaurant_project.routes.employee import employee_bp
from restaurant_project.routes.admin import admin_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'
app.config['SECRET_KEY'] = 'your-secret-key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(admin_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('employee.attendance'))

@app.cli.command('create-sample-data')
def create_sample_data():
    from restaurant_project.utils.sample_data import create_sample_users
    create_sample_users()
    print("샘플 유저 생성 완료")

@app.before_first_request
def create_tables():
    db.create_all()
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('templates/base.html'):
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>출근/퇴근 기록</title>
    <script src="//cdn.jsdelivr.net/npm/sweetalert2@11"></script>
</head>
<body>
    <nav>
        {% if current_user.is_authenticated and current_user.role == "employee" %}
            <a href="{{ url_for('employee.attendance') }}">출근/퇴근 기록</a>
            <a href="{{ url_for('auth.logout') }}">로그아웃</a>
        {% else %}
            <a href="{{ url_for('auth.login') }}">로그인</a>
        {% endif %}
    </nav>
    <hr>
    {% block content %}{% endblock %}
    <script>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          Swal.fire({
            icon: '{{ 'success' if category == 'success' else (category if category!="info" else "info") }}',
            title: '{{ message }}'
          });
        {% endfor %}
      {% endif %}
    {% endwith %}
    </script>
</body>
</html>
            ''')
    if not os.path.exists('templates/employee_attendance_multi.html'):
        with open('templates/employee_attendance_multi.html', 'w', encoding='utf-8') as f:
            f.write('''
{% extends "base.html" %}
{% block content %}
<h3>출근/퇴근 기록 (여러 번 입력 가능)</h3>
<form method="post">
    <button type="submit" name="action" value="clock_in">출근</button>
    <button type="submit" name="action" value="clock_out">퇴근</button>
</form>
<table border="1">
    <tr><th>출근</th><th>퇴근</th><th>근무시간(분)</th></tr>
    {% for r in records %}
    <tr>
        <td>{{ r.clock_in }}</td>
        <td>{{ r.clock_out if r.clock_out else "미입력" }}</td>
        <td>
            {% if r.clock_out %}
                {{ ((r.clock_out - r.clock_in).total_seconds() // 60) | int }}
            {% else %}
                -
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>
{% endblock %}
            ''')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 샘플 데이터 생성 등
    app.run(debug=True) 
    