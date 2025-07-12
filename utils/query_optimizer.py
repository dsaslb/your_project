#!/usr/bin/env python3
"""
데이터베이스 쿼리 최적화 시스템
쿼리 성능 분석, 인덱스 추천, 쿼리 캐싱, 연결 풀 관리
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import threading

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """쿼리 메트릭"""
    sql: str
    execution_time: float
    timestamp: datetime
    table_name: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE
    rows_affected: int
    parameters: Dict[str, Any]
    user_id: Optional[int] = None
    session_id: Optional[str] = None

@dataclass
class IndexRecommendation:
    """인덱스 추천"""
    table_name: str
    column_name: str
    index_type: str  # INDEX, UNIQUE, FULLTEXT
    reason: str
    estimated_improvement: float
    priority: int  # 1: 높음, 2: 중간, 3: 낮음

@dataclass
class QueryAnalysis:
    """쿼리 분석 결과"""
    query_id: str
    sql: str
    execution_count: int
    avg_execution_time: float
    total_execution_time: float
    slowest_execution: float
    fastest_execution: float
    last_executed: datetime
    table_scans: List[str]
    index_usage: Dict[str, str]
    recommendations: List[str]

class QueryOptimizer:
    """쿼리 최적화 시스템"""
    
    def __init__(self, db_engine, config: Optional[Dict[str, Any]] = None):
        self.db_engine = db_engine
        self.config = config or {}
        self.query_metrics = deque(maxlen=10000)  # 최근 10,000개 쿼리
        self.slow_query_threshold = self.config.get('slow_query_threshold', 1.0)  # 1초
        self.analysis_interval = self.config.get('analysis_interval', 3600)  # 1시간
        self.last_analysis = datetime.now()
        self.lock = threading.RLock()
        
        # 쿼리 분석 결과 캐시
        self.query_analysis_cache = {}
        self.index_recommendations = []
        
        # 성능 모니터링 활성화
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        
        logger.info("쿼리 최적화 시스템 초기화 완료")
    
    def start_monitoring(self):
        """쿼리 모니터링 시작"""
        if not self.monitoring_enabled:
            return
        
        # 데이터베이스 이벤트 리스너 등록
        from sqlalchemy import event
        
        @event.listens_for(self.db_engine, "before_cursor_execute")
        def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore # noqa
            context._query_start_time = time.time()
            context._query_sql = statement
            context._query_parameters = parameters
        
        @event.listens_for(self.db_engine, "after_cursor_execute")
        def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore # noqa
            execution_time = time.time() - context._query_start_time
            
            # 쿼리 메트릭 수집
            self._collect_query_metrics(
                statement, execution_time, parameters, context
            )
            
            # 느린 쿼리 로깅
            if execution_time > self.slow_query_threshold:
                logger.warning(f"느린 쿼리 감지: {execution_time:.3f}s - {statement[:100]}...")
        
        logger.info("쿼리 모니터링 시작")
    
    def _collect_query_metrics(self, sql: str, execution_time: float, 
                              parameters: Dict[str, Any], context):
        """쿼리 메트릭 수집"""
        try:
            # 쿼리 분석
            table_name = self._extract_table_name(sql)
            operation = self._extract_operation(sql)
            
            # 사용자 정보 추출 (가능한 경우)
            user_id = getattr(context, 'user_id', None)
            session_id = getattr(context, 'session_id', None)
            
            # 행 수 추정
            rows_affected = getattr(context, 'rowcount', 0)
            
            metric = QueryMetrics(
                sql=sql,
                execution_time=execution_time,
                timestamp=datetime.now(),
                table_name=table_name,
                operation=operation,
                rows_affected=rows_affected,
                parameters=parameters or {},
                user_id=user_id,
                session_id=session_id
            )
            
            with self.lock:
                self.query_metrics.append(metric)
                
        except Exception as e:
            logger.warning(f"쿼리 메트릭 수집 실패: {e}")
    
    def _extract_table_name(self, sql: str) -> str:
        """SQL에서 테이블명 추출"""
        try:
            sql_upper = sql.upper().strip()
            
            # FROM 절에서 테이블명 추출
            if 'FROM' in sql_upper:
                from_index = sql_upper.find('FROM')
                after_from = sql[from_index + 4:].strip()
                
                # 공백이나 괄호 전까지가 테이블명
                table_name = after_from.split()[0]
                return table_name.strip('`"[]')
            
            # INSERT INTO 절에서 테이블명 추출
            elif 'INSERT INTO' in sql_upper:
                insert_index = sql_upper.find('INSERT INTO')
                after_insert = sql[insert_index + 11:].strip()
                table_name = after_insert.split()[0]
                return table_name.strip('`"[]')
            
            # UPDATE 절에서 테이블명 추출
            elif 'UPDATE' in sql_upper:
                update_index = sql_upper.find('UPDATE')
                after_update = sql[update_index + 6:].strip()
                table_name = after_update.split()[0]
                return table_name.strip('`"[]')
            
            # DELETE FROM 절에서 테이블명 추출
            elif 'DELETE FROM' in sql_upper:
                delete_index = sql_upper.find('DELETE FROM')
                after_delete = sql[delete_index + 11:].strip()
                table_name = after_delete.split()[0]
                return table_name.strip('`"[]')
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def _extract_operation(self, sql: str) -> str:
        """SQL에서 작업 유형 추출"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def analyze_queries(self) -> Dict[str, Any]:
        """쿼리 분석 수행"""
        try:
            with self.lock:
                current_time = datetime.now()
                
                # 분석 간격 확인
                if (current_time - self.last_analysis).total_seconds() < self.analysis_interval:
                    return self.query_analysis_cache
                
                # 쿼리 그룹화
                query_groups = defaultdict(list)
                for metric in self.query_metrics:
                    # SQL 정규화 (파라미터 제거)
                    normalized_sql = self._normalize_sql(metric.sql)
                    query_groups[normalized_sql].append(metric)
                
                # 각 쿼리 그룹 분석
                analysis_results = []
                for sql, metrics in query_groups.items():
                    analysis = self._analyze_query_group(sql, metrics)
                    analysis_results.append(analysis)
                
                # 인덱스 추천 생성
                self._generate_index_recommendations(analysis_results)
                
                # 결과 캐시
                self.query_analysis_cache = {
                    'analysis_time': current_time.isoformat(),
                    'total_queries': len(self.query_metrics),
                    'unique_queries': len(analysis_results),
                    'slow_queries': len([a for a in analysis_results if a.avg_execution_time > self.slow_query_threshold]),
                    'queries': [asdict(a) for a in analysis_results],
                    'index_recommendations': [asdict(r) for r in self.index_recommendations]
                }
                
                self.last_analysis = current_time
                
                logger.info(f"쿼리 분석 완료: {len(analysis_results)}개 쿼리 분석")
                return self.query_analysis_cache
                
        except Exception as e:
            logger.error(f"쿼리 분석 실패: {e}")
            return {}
    
    def _normalize_sql(self, sql: str) -> str:
        """SQL 정규화 (파라미터 제거)"""
        try:
            # 기본적인 파라미터 패턴 제거
            import re
            
            # 숫자 리터럴을 ?로 대체
            sql = re.sub(r'\b\d+\b', '?', sql)
            
            # 문자열 리터럴을 ?로 대체
            sql = re.sub(r"'[^']*'", '?', sql)
            sql = re.sub(r'"[^"]*"', '?', sql)
            
            # 공백 정규화
            sql = re.sub(r'\s+', ' ', sql).strip()
            
            return sql
            
        except Exception:
            return sql
    
    def _analyze_query_group(self, sql: str, metrics: List[QueryMetrics]) -> QueryAnalysis:
        """쿼리 그룹 분석"""
        execution_times = [m.execution_time for m in metrics]
        
        analysis = QueryAnalysis(
            query_id=str(hash(sql) % 1000000),  # 간단한 해시를 문자열로 변환
            sql=sql,
            execution_count=len(metrics),
            avg_execution_time=sum(execution_times) / len(execution_times),
            total_execution_time=sum(execution_times),
            slowest_execution=max(execution_times),
            fastest_execution=min(execution_times),
            last_executed=max(m.timestamp for m in metrics),
            table_scans=self._detect_table_scans(sql),
            index_usage=self._analyze_index_usage(sql),
            recommendations=self._generate_query_recommendations(sql, metrics)
        )
        
        return analysis
    
    def _detect_table_scans(self, sql: str) -> List[str]:
        """테이블 스캔 감지"""
        table_scans = []
        
        # WHERE 절이 없는 SELECT 쿼리
        if 'SELECT' in sql.upper() and 'WHERE' not in sql.upper():
            table_name = self._extract_table_name(sql)
            if table_name != 'unknown':
                table_scans.append(table_name)
        
        # LIKE '%pattern%' 패턴 (앞에 와일드카드)
        if "LIKE '%" in sql.upper():
            table_name = self._extract_table_name(sql)
            if table_name != 'unknown':
                table_scans.append(f"{table_name} (LIKE pattern)")
        
        return table_scans
    
    def _analyze_index_usage(self, sql: str) -> Dict[str, str]:
        """인덱스 사용 분석"""
        index_usage = {}
        
        # WHERE 절에서 컬럼 분석
        if 'WHERE' in sql.upper():
            where_clause = sql.upper().split('WHERE')[1].split(('ORDER BY' if 'ORDER BY' in sql.upper() else 'GROUP BY' if 'GROUP BY' in sql.upper() else 'LIMIT' if 'LIMIT' in sql.upper() else ';'))[0]
            
            # 컬럼명 추출 (간단한 패턴 매칭)
            import re
            columns = re.findall(r'\b(\w+)\s*[=<>!]', where_clause)
            
            for column in columns:
                if column not in ['AND', 'OR', 'NOT', 'IN', 'IS', 'NULL']:
                    index_usage[column] = 'potential_index'
        
        return index_usage
    
    def _generate_query_recommendations(self, sql: str, metrics: List[QueryMetrics]) -> List[str]:
        """쿼리 최적화 추천 생성"""
        recommendations = []
        
        # 느린 쿼리 추천
        avg_time = sum(m.execution_time for m in metrics) / len(metrics)
        if avg_time > self.slow_query_threshold:
            recommendations.append("느린 쿼리: 인덱스 추가 또는 쿼리 최적화 필요")
        
        # 테이블 스캔 추천
        if self._detect_table_scans(sql):
            recommendations.append("테이블 스캔 감지: WHERE 절 추가 또는 인덱스 생성 필요")
        
        # SELECT * 추천
        if 'SELECT *' in sql.upper():
            recommendations.append("SELECT * 사용: 필요한 컬럼만 선택하도록 최적화")
        
        # LIMIT 없는 쿼리 추천
        if 'SELECT' in sql.upper() and 'LIMIT' not in sql.upper():
            recommendations.append("LIMIT 없음: 결과 수 제한 추가 고려")
        
        return recommendations
    
    def _generate_index_recommendations(self, analysis_results: List[QueryAnalysis]):
        """인덱스 추천 생성"""
        self.index_recommendations = []
        
        # 테이블별 컬럼 사용 빈도 분석
        column_usage = defaultdict(lambda: defaultdict(int))
        
        for analysis in analysis_results:
            for column, _ in analysis.index_usage.items():
                column_usage[analysis.table_scans[0] if analysis.table_scans else 'unknown'][column] += analysis.execution_count
        
        # 인덱스 추천 생성
        for table_name, columns in column_usage.items():
            if table_name == 'unknown':
                continue
            
            # 가장 많이 사용되는 컬럼들
            sorted_columns = sorted(columns.items(), key=lambda x: x[1], reverse=True)
            
            for column, usage_count in sorted_columns[:5]:  # 상위 5개
                if usage_count > 10:  # 10회 이상 사용된 컬럼만
                    recommendation = IndexRecommendation(
                        table_name=table_name,
                        column_name=column,
                        index_type='INDEX',
                        reason=f"쿼리에서 {usage_count}회 사용됨",
                        estimated_improvement=0.5,  # 50% 성능 향상 추정
                        priority=1 if usage_count > 50 else 2
                    )
                    self.index_recommendations.append(recommendation)
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """느린 쿼리 목록 조회"""
        try:
            with self.lock:
                slow_queries = [
                    metric for metric in self.query_metrics
                    if metric.execution_time > self.slow_query_threshold
                ]
                
                # 최근 순으로 정렬
                slow_queries.sort(key=lambda x: x.timestamp, reverse=True)
                
                return [
                    {
                        'sql': q.sql[:200] + '...' if len(q.sql) > 200 else q.sql,
                        'execution_time': q.execution_time,
                        'timestamp': q.timestamp.isoformat(),
                        'table_name': q.table_name,
                        'operation': q.operation
                    }
                    for q in slow_queries[:limit]
                ]
                
        except Exception as e:
            logger.error(f"느린 쿼리 조회 실패: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 조회"""
        try:
            with self.lock:
                if not self.query_metrics:
                    return {}
                
                execution_times = [m.execution_time for m in self.query_metrics]
                
                return {
                    'total_queries': len(self.query_metrics),
                    'avg_execution_time': sum(execution_times) / len(execution_times),
                    'max_execution_time': max(execution_times),
                    'min_execution_time': min(execution_times),
                    'slow_queries_count': len([t for t in execution_times if t > self.slow_query_threshold]),
                    'slow_query_percentage': (len([t for t in execution_times if t > self.slow_query_threshold]) / len(execution_times)) * 100,
                    'last_analysis': self.last_analysis.isoformat(),
                    'index_recommendations_count': len(self.index_recommendations)
                }
                
        except Exception as e:
            logger.error(f"성능 통계 조회 실패: {e}")
            return {}
    
    def clear_metrics(self):
        """메트릭 초기화"""
        with self.lock:
            self.query_metrics.clear()
            self.query_analysis_cache = {}
            self.index_recommendations = []
            logger.info("쿼리 메트릭 초기화 완료")

class ConnectionPoolOptimizer:
    """연결 풀 최적화"""
    
    def __init__(self, db_engine, config: Optional[Dict[str, Any]] = None):
        self.db_engine = db_engine
        self.config = config or {}
        self.original_pool = None
        self.optimized_pool = None
        
    def optimize_pool(self):
        """연결 풀 최적화"""
        try:
            # 최적화된 설정
            optimized_config = {
                'pool_size': self.config.get('pool_size', 20),
                'max_overflow': self.config.get('max_overflow', 30),
                'pool_timeout': self.config.get('pool_timeout', 30),
                'pool_recycle': self.config.get('pool_recycle', 3600),
                'pool_pre_ping': self.config.get('pool_pre_ping', True),
                'echo': self.config.get('echo', False)
            }
            
            # 새로운 엔진 생성
            url = str(self.db_engine.url)
            self.optimized_pool = create_engine(
                url,
                poolclass=QueuePool,
                **optimized_config
            )
            
            logger.info(f"연결 풀 최적화 완료: {optimized_config}")
            return self.optimized_pool
            
        except Exception as e:
            logger.error(f"연결 풀 최적화 실패: {e}")
            return None
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """연결 풀 통계 조회"""
        try:
            pool = self.db_engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid(),
                'total_connections': pool.size() + pool.overflow()
            }
            
        except Exception as e:
            logger.error(f"연결 풀 통계 조회 실패: {e}")
            return {}

# 전역 인스턴스
query_optimizer = None
connection_pool_optimizer = None

def initialize_query_optimizer(db_engine, config: Optional[Dict[str, Any]] = None):
    """쿼리 최적화 시스템 초기화"""
    global query_optimizer, connection_pool_optimizer
    
    query_optimizer = QueryOptimizer(db_engine, config)
    connection_pool_optimizer = ConnectionPoolOptimizer(db_engine, config)
    
    # 모니터링 시작
    query_optimizer.start_monitoring()
    
    return query_optimizer, connection_pool_optimizer

def get_query_optimizer() -> Optional[QueryOptimizer]:
    """쿼리 최적화 시스템 인스턴스 반환"""
    return query_optimizer

def get_connection_pool_optimizer() -> Optional[ConnectionPoolOptimizer]:
    """연결 풀 최적화 시스템 인스턴스 반환"""
    return connection_pool_optimizer 