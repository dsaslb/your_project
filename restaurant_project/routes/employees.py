from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

# 직원 등록 폼
@employees_bp.route('/register', methods=['GET', 'POST'])
def register_employee():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']  # 'employee', 'manager', 'admin'
        user = User(username=username, name=name, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        flash('직원 등록 완료')
        return redirect(url_for('employees.employee_list'))
    return render_template('employee_register.html')

# 직원 목록
@employees_bp.route('/list')
def employee_list():
    employees = User.query.all()
    return render_template('employee_list.html', employees=employees)
