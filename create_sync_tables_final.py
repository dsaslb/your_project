"""
동기화 테이블 생성 스크립트 (최종 버전)
- IdempotencyKey, SyncAudit, OutboxEvent 테이블 생성
- 기존 데이터베이스와 호환되도록 설계
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app
from extensions import db
from models_sync import IdempotencyKey, SyncAudit, OutboxEvent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sync_tables():
    """동기화 관련 테이블 생성"""
    try:
        with app.app_context():
            logger.info("🔄 동기화 테이블 생성 시작...")
            
            # 테이블 생성
            db.create_all()
            
            # 생성된 테이블 확인
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            sync_tables = ['idempotency_key', 'sync_audit', 'outbox_event']
            created_tables = [table for table in sync_tables if table in tables]
            
            logger.info(f"✅ 생성된 동기화 테이블: {created_tables}")
            
            # 테이블 구조 확인
            for table_name in created_tables:
                columns = inspector.get_columns(table_name)
                logger.info(f"📋 {table_name} 테이블 구조:")
                for col in columns:
                    logger.info(f"  - {col['name']}: {col['type']}")
            
            logger.info("🎉 동기화 테이블 생성 완료!")
            return True
            
    except Exception as e:
        logger.error(f"❌ 동기화 테이블 생성 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def verify_tables():
    """테이블 생성 확인"""
    try:
        with app.app_context():
            # 각 테이블에 샘플 데이터 삽입 테스트
            test_idem_key = "test-key-123"
            
            # IdempotencyKey 테스트
            idem = IdempotencyKey(key=test_idem_key)
            db.session.add(idem)
            db.session.commit()
            
            # 조회 테스트
            found = IdempotencyKey.query.get(test_idem_key)
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
            
            logger.info("🎉 모든 동기화 테이블 검증 완료!")
            return True
            
    except Exception as e:
        logger.error(f"❌ 테이블 검증 실패: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        return False

def main():
    """메인 실행 함수"""
    logger.info("🚀 동기화 테이블 생성 및 검증 시작")
    logger.info("=" * 60)
    
    # 1. 테이블 생성
    if not create_sync_tables():
        logger.error("테이블 생성 실패")
        return 1
    
    # 2. 테이블 검증
    if not verify_tables():
        logger.error("테이블 검증 실패")
        return 1
    
    logger.info("=" * 60)
    logger.info("🎉 모든 작업 완료! 동기화 시스템 준비 완료!")
    return 0

if __name__ == "__main__":
    exit(main())
