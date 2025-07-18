#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from extensions import db
from models_main import User
from app import app
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        try:
            db.create_all()
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print('기존 admin 계정이 있습니다. 비밀번호를 admin123으로 재설정합니다.')
                admin.password_hash = generate_password_hash('admin123')
                admin.role = 'admin'
                admin.email = 'admin@example.com'
                # admin.is_active = True  # property일 수 있으므로 주석 처리
                db.session.commit()
                print('admin 계정 비밀번호가 admin123으로 재설정되었습니다.')
            else:
                new_admin = User(
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    status='approved',
                    grade='ceo',
                    branch_id=None,
                    brand_id=None,
                    industry_id=None
                )
                db.session.add(new_admin)
                db.session.commit()
                print('admin 계정이 생성되었습니다. (비밀번호: admin123)')
        except Exception as e:
            db.session.rollback()
            print(f'admin 계정 생성 오류: {e}')

if __name__ == '__main__':
    create_admin() 