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
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        user_count = User.query.count()
        admin_user = User.query.filter_by(role='admin').first()
        result = {'status': 'healthy','user_count': user_count,'admin_exists': admin_user is not None,'admin_username': admin_user.username if admin_user else None}
        print('SUCCESS:' + json.dumps(result))
    except Exception as e:
        print('ERROR:' + str(e))
