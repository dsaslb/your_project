"""
데이터베이스 성능 최적화 도구
인덱스 최적화, 쿼리 튜닝, 성능 모니터링
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from sqlalchemy import text, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """데이터베이스 성능 최적화 관리자"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)
        
    def analyze_table_performance(self, table_name: str) -> Dict:
        """테이블 성능 분석"""
        try:
            session = self.Session()
            
            # 테이블 크기 분석
            size_query = text("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size(:table_name)) as total_size,
                    pg_size_pretty(pg_relation_size(:table_name)) as table_size,
                    pg_size_pretty(pg_total_relation_size(:table_name) - pg_relation_size(:table_name)) as index_size,
                    (SELECT count(*) FROM information_schema.tables WHERE table_name = :table_name) as exists
            """)
            
            result = session.execute(size_query, {'table_name': table_name})
            size_info = result.fetchone()
            
            # 행 수 분석
            count_query = text(f"SELECT COUNT(*) as row_count FROM {table_name}")
            count_result = session.execute(count_query)
            row_count = count_result.fetchone()[0]
            
            # 인덱스 분석
            indexes = self.inspector.get_indexes(table_name)
            
            # 통계 정보
            stats_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE tablename = :table_name
                ORDER BY n_distinct DESC
            """)
            
            stats_result = session.execute(stats_query, {'table_name': table_name})
            column_stats = [dict(row) for row in stats_result]
            
            session.close()
            
            return {
                'table_name': table_name,
                'total_size': size_info[0] if size_info else 'Unknown',
                'table_size': size_info[1] if size_info else 'Unknown',
                'index_size': size_info[2] if size_info else 'Unknown',
                'row_count': row_count,
                'indexes': indexes,
                'column_stats': column_stats
            }
            
        except SQLAlchemyError as e:
            logger.error(f"테이블 성능 분석 실패: {e}")
            return {}
    
    def find_slow_queries(self, limit: int = 10) -> List[Dict]:
        """느린 쿼리 찾기"""
        try:
            session = self.Session()
            
            # PostgreSQL 느린 쿼리 로그 분석
            slow_query = text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    shared_blks_hit,
                    shared_blks_read,
                    shared_blks_written,
                    shared_blks_dirtied,
                    temp_blks_read,
                    temp_blks_written,
                    blk_read_time,
                    blk_write_time
                FROM pg_stat_statements 
                ORDER BY mean_time DESC 
                LIMIT :limit
            """)
            
            result = session.execute(slow_query, {'limit': limit})
            slow_queries = [dict(row) for row in result]
            
            session.close()
            return slow_queries
            
        except SQLAlchemyError as e:
            logger.error(f"느린 쿼리 분석 실패: {e}")
            return []
    
    def analyze_index_usage(self) -> Dict:
        """인덱스 사용량 분석"""
        try:
            session = self.Session()
            
            # 인덱스 사용 통계
            index_usage_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC
            """)
            
            result = session.execute(index_usage_query)
            index_usage = [dict(row) for row in result]
            
            # 사용되지 않는 인덱스 찾기
            unused_indexes_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                FROM pg_stat_user_indexes 
                WHERE idx_scan = 0
                ORDER BY pg_relation_size(indexrelid) DESC
            """)
            
            unused_result = session.execute(unused_indexes_query)
            unused_indexes = [dict(row) for row in unused_result]
            
            session.close()
            
            return {
                'index_usage': index_usage,
                'unused_indexes': unused_indexes
            }
            
        except SQLAlchemyError as e:
            logger.error(f"인덱스 사용량 분석 실패: {e}")
            return {}
    
    def suggest_indexes(self, table_name: str) -> List[Dict]:
        """인덱스 제안"""
        try:
            session = self.Session()
            
            # WHERE 절에서 자주 사용되는 컬럼 분석
            where_columns_query = text("""
                SELECT 
                    attname,
                    n_distinct,
                    correlation,
                    most_common_vals,
                    most_common_freqs
                FROM pg_stats 
                WHERE tablename = :table_name
                ORDER BY n_distinct DESC
            """)
            
            result = session.execute(where_columns_query, {'table_name': table_name})
            column_stats = [dict(row) for row in result]
            
            # 기존 인덱스 확인
            existing_indexes = self.inspector.get_indexes(table_name)
            indexed_columns = set()
            
            for index in existing_indexes:
                indexed_columns.update(index['column_names'])
            
            # 인덱스 제안
            suggestions = []
            
            for column in column_stats:
                if column['attname'] not in indexed_columns:
                    # 높은 카디널리티 컬럼에 인덱스 제안
                    if column['n_distinct'] and column['n_distinct'] > 100:
                        suggestions.append({
                            'column': column['attname'],
                            'type': 'B-tree',
                            'reason': f"높은 카디널리티 ({column['n_distinct']} distinct values)",
                            'priority': 'high' if column['n_distinct'] > 1000 else 'medium'
                        })
            
            session.close()
            return suggestions
            
        except SQLAlchemyError as e:
            logger.error(f"인덱스 제안 실패: {e}")
            return []
    
    def create_index(self, table_name: str, column_name: str, index_type: str = 'btree') -> bool:
        """인덱스 생성"""
        try:
            session = self.Session()
            
            index_name = f"idx_{table_name}_{column_name}"
            
            create_index_query = text(f"""
                CREATE INDEX {index_name} 
                ON {table_name} 
                USING {index_type} ({column_name})
            """)
            
            session.execute(create_index_query)
            session.commit()
            session.close()
            
            logger.info(f"인덱스 생성 완료: {index_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"인덱스 생성 실패: {e}")
            return False
    
    def drop_unused_index(self, index_name: str) -> bool:
        """사용되지 않는 인덱스 삭제"""
        try:
            session = self.Session()
            
            drop_index_query = text(f"DROP INDEX IF EXISTS {index_name}")
            session.execute(drop_index_query)
            session.commit()
            session.close()
            
            logger.info(f"인덱스 삭제 완료: {index_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"인덱스 삭제 실패: {e}")
            return False
    
    def analyze_query_performance(self, query: str) -> Dict:
        """쿼리 성능 분석"""
        try:
            session = self.Session()
            
            # EXPLAIN ANALYZE 실행
            explain_query = text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
            result = session.execute(explain_query)
            
            # 실행 계획 분석
            execution_plan = result.fetchone()[0]
            
            # 성능 메트릭 추출
            performance_metrics = self._extract_performance_metrics(execution_plan)
            
            session.close()
            
            return {
                'query': query,
                'execution_plan': execution_plan,
                'performance_metrics': performance_metrics
            }
            
        except SQLAlchemyError as e:
            logger.error(f"쿼리 성능 분석 실패: {e}")
            return {}
    
    def _extract_performance_metrics(self, execution_plan: List) -> Dict:
        """실행 계획에서 성능 메트릭 추출"""
        metrics = {
            'total_cost': 0,
            'total_time': 0,
            'total_rows': 0,
            'shared_hit_blocks': 0,
            'shared_read_blocks': 0,
            'shared_written_blocks': 0
        }
        
        def extract_from_node(node):
            if isinstance(node, dict):
                # 비용 정보
                if 'Total Cost' in node:
                    metrics['total_cost'] += float(node['Total Cost'])
                if 'Actual Total Time' in node:
                    metrics['total_time'] += float(node['Actual Total Time'])
                if 'Actual Rows' in node:
                    metrics['total_rows'] += int(node['Actual Rows'])
                
                # 블록 정보
                if 'Shared Hit Blocks' in node:
                    metrics['shared_hit_blocks'] += int(node['Shared Hit Blocks'])
                if 'Shared Read Blocks' in node:
                    metrics['shared_read_blocks'] += int(node['Shared Read Blocks'])
                if 'Shared Written Blocks' in node:
                    metrics['shared_written_blocks'] += int(node['Shared Written Blocks'])
                
                # 하위 노드 재귀 처리
                if 'Plans' in node:
                    for sub_node in node['Plans']:
                        extract_from_node(sub_node)
        
        for node in execution_plan:
            extract_from_node(node)
        
        return metrics
    
    def optimize_table(self, table_name: str) -> Dict:
        """테이블 최적화"""
        try:
            session = self.Session()
            
            # VACUUM 실행
            vacuum_query = text(f"VACUUM ANALYZE {table_name}")
            session.execute(vacuum_query)
            
            # 통계 업데이트
            analyze_query = text(f"ANALYZE {table_name}")
            session.execute(analyze_query)
            
            session.commit()
            session.close()
            
            logger.info(f"테이블 최적화 완료: {table_name}")
            
            return {
                'table_name': table_name,
                'optimization': 'VACUUM ANALYZE completed',
                'status': 'success'
            }
            
        except SQLAlchemyError as e:
            logger.error(f"테이블 최적화 실패: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_database_stats(self) -> Dict:
        """데이터베이스 전체 통계"""
        try:
            session = self.Session()
            
            # 데이터베이스 크기
            db_size_query = text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as database_size,
                    pg_size_pretty(pg_total_relation_size('pg_stat_statements')) as stats_size
            """)
            
            db_size_result = session.execute(db_size_query)
            db_size = dict(db_size_result.fetchone())
            
            # 연결 수
            connections_query = text("""
                SELECT 
                    count(*) as active_connections,
                    max_conn as max_connections
                FROM pg_stat_activity, pg_settings 
                WHERE name = 'max_connections'
            """)
            
            connections_result = session.execute(connections_query)
            connections = dict(connections_result.fetchone())
            
            # 캐시 히트율
            cache_query = text("""
                SELECT 
                    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
                FROM pg_statio_user_tables
            """)
            
            cache_result = session.execute(cache_query)
            cache_hit = cache_result.fetchone()[0] or 0
            
            session.close()
            
            return {
                'database_size': db_size['database_size'],
                'stats_size': db_size['stats_size'],
                'active_connections': connections['active_connections'],
                'max_connections': connections['max_connections'],
                'cache_hit_ratio': round(cache_hit, 2)
            }
            
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 통계 수집 실패: {e}")
            return {}
    
    def generate_optimization_report(self) -> Dict:
        """최적화 리포트 생성"""
        try:
            # 전체 통계
            db_stats = self.get_database_stats()
            
            # 느린 쿼리
            slow_queries = self.find_slow_queries(5)
            
            # 인덱스 사용량
            index_usage = self.analyze_index_usage()
            
            # 주요 테이블 성능 분석
            main_tables = ['users', 'brands', 'branches', 'employees', 'attendance_records']
            table_performance = {}
            
            for table in main_tables:
                try:
                    table_performance[table] = self.analyze_table_performance(table)
                except:
                    continue
            
            return {
                'database_stats': db_stats,
                'slow_queries': slow_queries,
                'index_usage': index_usage,
                'table_performance': table_performance,
                'recommendations': self._generate_recommendations(db_stats, slow_queries, index_usage)
            }
            
        except Exception as e:
            logger.error(f"최적화 리포트 생성 실패: {e}")
            return {}
    
    def _generate_recommendations(self, db_stats: Dict, slow_queries: List, index_usage: Dict) -> List[str]:
        """최적화 권장사항 생성"""
        recommendations = []
        
        # 캐시 히트율 권장사항
        if db_stats.get('cache_hit_ratio', 100) < 90:
            recommendations.append("캐시 히트율이 낮습니다. shared_buffers를 증가시키거나 자주 사용되는 쿼리에 인덱스를 추가하세요.")
        
        # 느린 쿼리 권장사항
        if slow_queries:
            recommendations.append(f"{len(slow_queries)}개의 느린 쿼리가 발견되었습니다. 쿼리 최적화나 인덱스 추가를 고려하세요.")
        
        # 사용되지 않는 인덱스 권장사항
        unused_count = len(index_usage.get('unused_indexes', []))
        if unused_count > 0:
            recommendations.append(f"{unused_count}개의 사용되지 않는 인덱스가 있습니다. 삭제를 고려하세요.")
        
        # 연결 수 권장사항
        active_connections = db_stats.get('active_connections', 0)
        max_connections = db_stats.get('max_connections', 100)
        if active_connections > max_connections * 0.8:
            recommendations.append("활성 연결 수가 많습니다. 연결 풀 설정을 확인하세요.")
        
        return recommendations

# 전역 데이터베이스 최적화 인스턴스
db_optimizer = None

def init_database_optimizer(database_url: str):
    """데이터베이스 최적화 도구 초기화"""
    global db_optimizer
    db_optimizer = DatabaseOptimizer(database_url)
    logger.info("데이터베이스 최적화 도구 초기화 완료")

def get_database_optimizer() -> Optional[DatabaseOptimizer]:
    """데이터베이스 최적화 도구 반환"""
    return db_optimizer 