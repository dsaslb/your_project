import datetime
from models import AuditLog, db
from flask_login import current_user

# 감사 로그 자동 기록 유틸리티
# 사용 예시: audit_log('조회', 'SystemLog', 123)
def audit_log(action, model_name, object_id, detail=None):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        model=model_name,
        object_id=object_id,
        detail=detail,
        timestamp=datetime.datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit() 