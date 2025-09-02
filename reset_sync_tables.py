"""
동기화 테이블 리셋 스크립트
- 기존 동기화 테이블 삭제 후 재생성
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app
from extensions import db
from models_sync import IdempotencyKey, SyncAudit, OutboxEvent, SyncMetrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_sync_tables():
    """동기화 테이블 리셋"""
    try:
        with app.app_context():
            logger.info("🔄 동기화 테이블 리셋 시작...")
            
            # 기존 테이블 삭제
            try:
                OutboxEvent.__table__.drop(db.engine, checkfirst=True)
                SyncAudit.__table__.drop(db.engine, checkfirst=True)
                IdempotencyKey.__table__.drop(db.engine, checkfirst=True)
                SyncMetrics.__table__.drop(db.engine, checkfirst=True)
                logger.info("✅ 기존 동기화 테이블 삭제 완료")
            except Exception as e:
                logger.warning(f"기존 테이블 삭제 중 오류 (무시됨): {e}")
            
            # 새 테이블 생성
            db.create_all()
            logger.info("✅ 새 동기화 테이블 생성 완료")
            
            # 테이블 구조 확인
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            sync_tables = ['idempotency_keys', 'sync_audits', 'outbox_events', 'sync_metrics']
            created_tables = [table for table in sync_tables if table in tables]
            
            logger.info(f"📋 생성된 동기화 테이블: {created_tables}")
            
            # 각 테이블의 컬럼 정보 출력
            for table_name in created_tables:
                columns = inspector.get_columns(table_name)
                logger.info(f"📋 {table_name} 테이블 구조:")
                for col in columns:
                    logger.info(f"  - {col['name']}: {col['type']} {'(nullable=False)' if not col['nullable'] else ''}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ 동기화 테이블 리셋 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def test_tables():
    """테이블 테스트"""
    try:
        with app.app_context():
            logger.info("🧪 테이블 기능 테스트 시작...")
            
            # IdempotencyKey 테스트
            test_key = "test-key-123"
            idem = IdempotencyKey(key=test_key)
            db.session.add(idem)
            db.session.commit()
            
            found = IdempotencyKey.query.get(test_key)
            if found:
                logger.info("✅ IdempotencyKey 테이블 정상 작동")
                db.session.delete(found)
                db.session.commit()
            else:
                logger.error("❌ IdempotencyKey 테이블 조회 실패")
                return False
            
            # SyncAudit 테스트
            audit = SyncAudit(
                user_id=1,
                device_id="test-device",
                type="test",
                idem_key="test-audit-123",
                status="ok"
            )
            db.session.add(audit)
            db.session.commit()
            
            found_audit = SyncAudit.query.filter_by(idem_key="test-audit-123").first()
            if found_audit:
                logger.info("✅ SyncAudit 테이블 정상 작동")
                db.session.delete(found_audit)
                db.session.commit()
            else:
                logger.error("❌ SyncAudit 테이블 조회 실패")
                return False
            
            # OutboxEvent 테스트
            event = OutboxEvent(
                channel="test:event",
                payload={"test": "data"},
                delivered=False
            )
            db.session.add(event)
            db.session.commit()
            
            found_event = OutboxEvent.query.filter_by(channel="test:event").first()
            if found_event:
                logger.info("✅ OutboxEvent 테이블 정상 작동")
                db.session.delete(found_event)
                db.session.commit()
            else:
                logger.error("❌ OutboxEvent 테이블 조회 실패")
                return False
            
            logger.info("🎉 모든 테이블 테스트 통과!")
            return True
            
    except Exception as e:
        logger.error(f"❌ 테이블 테스트 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def main():
    """메인 실행 함수"""
    logger.info("🚀 동기화 테이블 리셋 및 테스트 시작")
    logger.info("=" * 60)
    
    # 1. 테이블 리셋
    if not reset_sync_tables():
        logger.error("테이블 리셋 실패")
        return 1
    
    # 2. 테이블 테스트
    if not test_tables():
        logger.error("테이블 테스트 실패")
        return 1
    
    logger.info("=" * 60)
    logger.info("🎉 모든 작업 완료! 동기화 시스템 준비 완료!")
    return 0

if __name__ == "__main__":
    exit(main())
