"""
고급 데이터베이스 마이그레이션 시스템
데이터 무결성 검사, 롤백 지원, 성능 최적화
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from extensions import db

logger = logging.getLogger(__name__)


class AdvancedMigration:
    """고급 마이그레이션 관리자"""
    
    def __init__(self):
        self.migration_history = []
        self.backup_tables = []
        self.performance_metrics = {}
    
    def create_backup(self, table_name: str) -> bool:
        """테이블 백업 생성"""
        try:
            backup_table = f"{table_name}_backup_{int(time.time())}"
            
            # 테이블 구조 및 데이터 복사
            db.session.execute(text(f"""
                CREATE TABLE {backup_table} AS 
                SELECT * FROM {table_name}
            """))
            
            # 인덱스 복사
            db.session.execute(text(f"""
                CREATE INDEX idx_{backup_table}_id 
                ON {backup_table} (id)
            """))
            
            db.session.commit()
            self.backup_tables.append(backup_table)
            
            logger.info(f"테이블 백업 생성 완료: {table_name} -> {backup_table}")
            return True
            
        except Exception as e:
            logger.error(f"백업 생성 실패: {e}")
            db.session.rollback()
            return False
    
    def restore_backup(self, table_name: str, backup_table: str) -> bool:
        """백업에서 복원"""
        try:
            # 기존 테이블 삭제
            db.session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            
            # 백업 테이블을 원래 이름으로 변경
            db.session.execute(text(f"""
                ALTER TABLE {backup_table} 
                RENAME TO {table_name}
            """))
            
            db.session.commit()
            logger.info(f"백업 복원 완료: {backup_table} -> {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"백업 복원 실패: {e}")
            db.session.rollback()
            return False
    
    def validate_data_integrity(self, table_name: str) -> Dict[str, Any]:
        """데이터 무결성 검사"""
        try:
            # NULL 값 검사
            null_check = db.session.execute(text(f"""
                SELECT COUNT(*) as null_count 
                FROM {table_name} 
                WHERE id IS NULL
            """)).fetchone()
            
            # 중복 키 검사
            duplicate_check = db.session.execute(text(f"""
                SELECT id, COUNT(*) as count 
                FROM {table_name} 
                GROUP BY id 
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            # 외래 키 무결성 검사
            foreign_key_check = db.session.execute(text(f"""
                SELECT COUNT(*) as fk_violations
                FROM {table_name} t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.user_id IS NOT NULL AND u.id IS NULL
            """)).fetchone()
            
            return {
                'table_name': table_name,
                'null_violations': null_check.null_count,
                'duplicate_keys': len(duplicate_check),
                'foreign_key_violations': foreign_key_check.fk_violations,
                'is_valid': (null_check.null_count == 0 and 
                           len(duplicate_check) == 0 and 
                           foreign_key_check.fk_violations == 0)
            }
            
        except Exception as e:
            logger.error(f"데이터 무결성 검사 실패: {e}")
            return {'error': str(e)}
    
    def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """테이블 최적화"""
        try:
            start_time = time.time()
            
            # 테이블 분석
            db.session.execute(text(f"ANALYZE {table_name}"))
            
            # 인덱스 재구성
            db.session.execute(text(f"REINDEX TABLE {table_name}"))
            
            # VACUUM 실행
            db.session.execute(text(f"VACUUM {table_name}"))
            
            execution_time = time.time() - start_time
            
            # 최적화 결과 확인
            table_size = db.session.execute(text(f"""
                SELECT pg_total_relation_size('{table_name}') as size
            """)).fetchone()
            
            return {
                'table_name': table_name,
                'execution_time': execution_time,
                'table_size': table_size.size,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"테이블 최적화 실패: {e}")
            return {'error': str(e)}
    
    def create_indexes(self) -> Dict[str, Any]:
        """성능 향상을 위한 인덱스 생성"""
        try:
            indexes = [
                # 사용자 테이블 인덱스
                "CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users(LOWER(email))",
                "CREATE INDEX IF NOT EXISTS idx_users_role_status ON users(role, status)",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
                
                # 브랜드 테이블 인덱스
                "CREATE INDEX IF NOT EXISTS idx_brands_industry_id ON brands(industry_id)",
                "CREATE INDEX IF NOT EXISTS idx_brands_status ON brands(status)",
                "CREATE INDEX IF NOT EXISTS idx_brands_created_at ON brands(created_at)",
                
                # 매장 테이블 인덱스
                "CREATE INDEX IF NOT EXISTS idx_branches_brand_id ON branches(brand_id)",
                "CREATE INDEX IF NOT EXISTS idx_branches_industry_id ON branches(industry_id)",
                "CREATE INDEX IF NOT EXISTS idx_branches_status ON branches(status)",
                
                # 복합 인덱스
                "CREATE INDEX IF NOT EXISTS idx_users_branch_role ON users(branch_id, role)",
                "CREATE INDEX IF NOT EXISTS idx_branches_brand_status ON branches(brand_id, status)"
            ]
            
            created_count = 0
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    created_count += 1
                except Exception as e:
                    logger.warning(f"인덱스 생성 실패: {index_sql} - {e}")
            
            db.session.commit()
            
            return {
                'total_indexes': len(indexes),
                'created_count': created_count,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {e}")
            db.session.rollback()
            return {'error': str(e)}
    
    def partition_large_tables(self) -> Dict[str, Any]:
        """대용량 테이블 파티셔닝"""
        try:
            # 파티셔닝 대상 테이블 확인
            large_tables = db.session.execute(text("""
                SELECT tablename, pg_total_relation_size(tablename::regclass) as size
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND pg_total_relation_size(tablename::regclass) > 100000000
                ORDER BY size DESC
            """)).fetchall()
            
            partitioned_tables = []
            for table in large_tables:
                if table.size > 100000000:  # 100MB 이상
                    # 월별 파티셔닝 예시
                    partition_sql = f"""
                    CREATE TABLE {table.tablename}_2024_01 PARTITION OF {table.tablename}
                    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
                    """
                    
                    try:
                        db.session.execute(text(partition_sql))
                        partitioned_tables.append(table.tablename)
                    except Exception as e:
                        logger.warning(f"파티셔닝 실패: {table.tablename} - {e}")
            
            db.session.commit()
            
            return {
                'large_tables': len(large_tables),
                'partitioned_tables': partitioned_tables,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"파티셔닝 실패: {e}")
            db.session.rollback()
            return {'error': str(e)}
    
    def cleanup_old_data(self, days: int = 90) -> Dict[str, Any]:
        """오래된 데이터 정리"""
        try:
            cleanup_date = datetime.utcnow() - timedelta(days=days)
            
            # 정리 대상 테이블들
            cleanup_queries = [
                f"DELETE FROM logs WHERE created_at < '{cleanup_date.isoformat()}'",
                f"DELETE FROM audit_logs WHERE timestamp < '{cleanup_date.isoformat()}'",
                f"DELETE FROM temp_files WHERE created_at < '{cleanup_date.isoformat()}'"
            ]
            
            deleted_counts = {}
            for query in cleanup_queries:
                try:
                    result = db.session.execute(text(query))
                    table_name = query.split('FROM ')[1].split(' ')[0]
                    deleted_counts[table_name] = result.rowcount
                except Exception as e:
                    logger.warning(f"데이터 정리 실패: {query} - {e}")
            
            db.session.commit()
            
            return {
                'cleanup_date': cleanup_date.isoformat(),
                'deleted_counts': deleted_counts,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")
            db.session.rollback()
            return {'error': str(e)}
    
    def get_migration_report(self) -> Dict[str, Any]:
        """마이그레이션 리포트 생성"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'backup_tables': self.backup_tables,
            'performance_metrics': self.performance_metrics,
            'migration_history': self.migration_history
        }


# 전역 마이그레이션 인스턴스
advanced_migration = AdvancedMigration()


def run_advanced_migration():
    """고급 마이그레이션 실행"""
    from app import app
    
    with app.app_context():
        logger.info("고급 마이그레이션 시작")
        
        # 1. 인덱스 생성
        index_result = advanced_migration.create_indexes()
        logger.info(f"인덱스 생성 결과: {index_result}")
        
        # 2. 데이터 무결성 검사
        tables = ['users', 'brands', 'branches']
        for table in tables:
            integrity_result = advanced_migration.validate_data_integrity(table)
            logger.info(f"데이터 무결성 검사 결과 ({table}): {integrity_result}")
        
        # 3. 테이블 최적화
        for table in tables:
            optimize_result = advanced_migration.optimize_table(table)
            logger.info(f"테이블 최적화 결과 ({table}): {optimize_result}")
        
        # 4. 오래된 데이터 정리
        cleanup_result = advanced_migration.cleanup_old_data()
        logger.info(f"데이터 정리 결과: {cleanup_result}")
        
        logger.info("고급 마이그레이션 완료")
        return advanced_migration.get_migration_report() 