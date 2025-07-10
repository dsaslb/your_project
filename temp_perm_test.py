import sys
import os
import logging
import json
sys.path.append(os.path.dirname(os.path.abspath('.')))

# WARNING ??遺덊븘?뷀븳 異쒕젰 ?쒓굅
logging.getLogger().setLevel(logging.ERROR)
os.environ['WARNING'] = '0'

from app import app, db
from models import User

with app.app_context():
    try:
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print('ERROR: Admin user not found')
            exit(1)
        permissions = admin_user.permissions if admin_user.permissions else {}
        test_results = {'has_dashboard': admin_user.has_permission('dashboard', 'view'),'has_employee_management': admin_user.has_permission('employee_management', 'view'),'can_access_module': admin_user.can_access_module('dashboard'),'permission_count': len(permissions),'role': admin_user.role}
        print('SUCCESS:' + json.dumps(test_results))
    except Exception as e:
        print('ERROR:' + str(e))
