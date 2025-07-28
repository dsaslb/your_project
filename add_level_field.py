from app import app
from extensions import db

with app.app_context():
    try:
        # SystemLog 테이블에 level 필드 추가
        db.engine.execute('ALTER TABLE system_logs ADD COLUMN level VARCHAR(20) DEFAULT "info"')
        print('SystemLog 테이블에 level 필드 추가 완료')
    except Exception as e:
        print(f'필드 추가 중 오류 발생: {e}')
        # 이미 필드가 존재하는 경우 무시
        if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
            print('level 필드가 이미 존재합니다.')
        else:
            raise e 