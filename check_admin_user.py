#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from extensions import db
from models_main import User
from app import app

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"username: {admin.username}")
        print(f"password_hash: {admin.password_hash}")
        print(f"role: {getattr(admin, 'role', None)}")
        print(f"is_active: {getattr(admin, 'is_active', None)}")
    else:
        print("admin 계정이 존재하지 않습니다.") 