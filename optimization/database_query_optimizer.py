#!/usr/bin/env python3
"""
🗄️ Your Program 데이터베이스 쿼리 최적화 시스템

실시간으로 데이터베이스 쿼리 성능을 모니터링하고 분석하여
자동으로 최적화 제안과 인덱스 생성을 수행하는 지능형 시스템입니다.

주요 기능:
- 실시간 쿼리 성능 모니터링
- 슬로우 쿼리 자동 감지 및 분석
- 인덱스 최적화 제안 및 자동 생성
- 쿼리 실행 계획 분석
- 데이터베이스 통계 수집 및 분석
- 자동 VACUUM 및 ANALYZE
"""

import asyncio
import json
import logging
import time
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import redis
from pathlib import Path
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QueryStats:
    """쿼리 통계 정보"""
    query_hash: str
    query_text: str
    normalized_query: str
    execution_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    rows_examined: int
    rows_returned: int
    first_seen: datetime
    last_seen: datetime
    database_name: str
    table_names: List[str]

@dataclass
class SlowQuery:
    """슬로우 쿼리 정보"""
    query_hash: str
    query_text: str
    execution_time: float
    timestamp: datetime
    database_name: str
    table_names: List[str]
    explain_plan: Optional[Dict[str, Any]]
    optimization_suggestions: List[str]

@dataclass
class IndexSuggestion:
    """인덱스 제안"""
    table_name: str
    column_names: List[str]
    index_type: str  # 'btree', 'hash', 'gin', 'gist'
    estimated_benefit: float
    current_cost: float
    estimated_cost: float
    justification: str
    query_patterns: List[str]

@dataclass
class OptimizationResult:
    """최적화 결과"""
    optimization_id: str
    optimization_type: str
    target_query: str
    action_taken: str
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    improvement_percentage: float
    execution_time: datetime
    success: bool

class DatabaseQueryOptimizer:
    """데이터베이스 쿼리 최적화 시스템"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
        
        # 데이터 저장소
        self.data_path = "optimization/query_optimizer.db"
        self.query_stats: Dict[str, QueryStats] = {}
        self.slow_queries: List[SlowQuery] = []
        self.index_suggestions: List[IndexSuggestion] = []
        
        # 설정
        self.slow_query_threshold = 1.0  # 1초 이상
        self.monitoring_enabled = True
        self.auto_optimize = True
        self.max_slow_queries = 1000
        
        self.init_storage()
        
    def init_storage(self):
        """저장소 초기화"""
        Path(self.data_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        # 쿼리 통계 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_stats (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT,
                normalized_query TEXT,
                execution_count INTEGER,
                total_time REAL,
                avg_time REAL,
                min_time REAL,
                max_time REAL,
                rows_examined INTEGER,
                rows_returned INTEGER,
                first_seen TEXT,
                last_seen TEXT,
                database_name TEXT,
                table_names TEXT
            )
        """)
        
        # 슬로우 쿼리 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slow_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT,
                query_text TEXT,
                execution_time REAL,
                timestamp TEXT,
                database_name TEXT,
                table_names TEXT,
                explain_plan TEXT,
                optimization_suggestions TEXT
            )
        """)
        
        # 인덱스 제안 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS index_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT,
                column_names TEXT,
                index_type TEXT,
                estimated_benefit REAL,
                current_cost REAL,
                estimated_cost REAL,
                justification TEXT,
                query_patterns TEXT,
                created_timestamp TEXT,
                applied BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 최적화 결과 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_results (
                optimization_id TEXT PRIMARY KEY,
                optimization_type TEXT,
                target_query TEXT,
                action_taken TEXT,
                before_metrics TEXT,
                after_metrics TEXT,
                improvement_percentage REAL,
                execution_time TEXT,
                success BOOLEAN
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def start_monitoring(self):
        """모니터링 시작"""
        logger.info("🗄️ 데이터베이스 쿼리 최적화 시스템 시작")
        
        tasks = [
            asyncio.create_task(self._monitor_queries()),
            asyncio.create_task(self._analyze_slow_queries()),
            asyncio.create_task(self._generate_index_suggestions()),
            asyncio.create_task(self._auto_optimize()),
            asyncio.create_task(self._maintenance_tasks()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _monitor_queries(self):
        """쿼리 모니터링"""
        while self.monitoring_enabled:
            try:
                # PostgreSQL 쿼리 로그 모니터링
                await self._monitor_postgresql_queries()
                
                # 통계 업데이트
                await self._update_query_statistics()
                
                await asyncio.sleep(30)  # 30초마다 모니터링
                
            except Exception as e:
                logger.error(f"쿼리 모니터링 오류: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_postgresql_queries(self):
        """PostgreSQL 쿼리 모니터링"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # pg_stat_statements 확장이 있는 경우 활용
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                )
            """)
            
            has_pg_stat_statements = cursor.fetchone()[0]
            
            if has_pg_stat_statements:
                await self._monitor_with_pg_stat_statements(cursor)
            else:
                await self._monitor_with_pg_stat_activity(cursor)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"PostgreSQL 모니터링 오류: {e}")
    
    async def _monitor_with_pg_stat_statements(self, cursor):
        """pg_stat_statements를 사용한 모니터링"""
        cursor.execute("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                min_time,
                max_time,
                rows
            FROM pg_stat_statements 
            WHERE mean_time > %s
            ORDER BY mean_time DESC
            LIMIT 100
        """, (self.slow_query_threshold * 1000,))  # 밀리초 단위
        
        results = cursor.fetchall()
        
        for row in results:
            query_text = row[0]
            calls = row[1]
            total_time = row[2] / 1000.0  # 초 단위로 변환
            mean_time = row[3] / 1000.0
            min_time = row[4] / 1000.0
            max_time = row[5] / 1000.0
            rows = row[6]
            
            await self._process_query_stats(
                query_text, calls, total_time, mean_time, 
                min_time, max_time, rows, 0
            )
    
    async def _monitor_with_pg_stat_activity(self, cursor):
        """pg_stat_activity를 사용한 기본 모니터링"""
        cursor.execute("""
            SELECT 
                query,
                state,
                query_start,
                state_change
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND query NOT LIKE '%pg_stat_activity%'
            AND query_start IS NOT NULL
        """)
        
        results = cursor.fetchall()
        current_time = datetime.now()
        
        for row in results:
            query_text = row[0]
            query_start = row[2]
            
            if query_start:
                execution_time = (current_time - query_start.replace(tzinfo=None)).total_seconds()
                
                if execution_time > self.slow_query_threshold:
                    await self._process_slow_query(query_text, execution_time)
    
    async def _process_query_stats(self, query_text: str, calls: int, total_time: float,
                                 avg_time: float, min_time: float, max_time: float,
                                 rows_examined: int, rows_returned: int):
        """쿼리 통계 처리"""
        try:
            # 쿼리 정규화 및 해시 생성
            normalized_query = self._normalize_query(query_text)
            query_hash = self._hash_query(normalized_query)
            
            # 테이블 이름 추출
            table_names = self._extract_table_names(query_text)
            
            # 통계 업데이트
            if query_hash in self.query_stats:
                stats = self.query_stats[query_hash]
                stats.execution_count += calls
                stats.total_time += total_time
                stats.avg_time = stats.total_time / stats.execution_count
                stats.min_time = min(stats.min_time, min_time)
                stats.max_time = max(stats.max_time, max_time)
                stats.last_seen = datetime.now()
            else:
                stats = QueryStats(
                    query_hash=query_hash,
                    query_text=query_text,
                    normalized_query=normalized_query,
                    execution_count=calls,
                    total_time=total_time,
                    avg_time=avg_time,
                    min_time=min_time,
                    max_time=max_time,
                    rows_examined=rows_examined,
                    rows_returned=rows_returned,
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    database_name=self.db_config.get('database', 'unknown'),
                    table_names=table_names
                )
                self.query_stats[query_hash] = stats
            
            # 슬로우 쿼리 감지
            if avg_time > self.slow_query_threshold:
                await self._process_slow_query(query_text, avg_time)
            
        except Exception as e:
            logger.error(f"쿼리 통계 처리 오류: {e}")
    
    async def _process_slow_query(self, query_text: str, execution_time: float):
        """슬로우 쿼리 처리"""
        try:
            normalized_query = self._normalize_query(query_text)
            query_hash = self._hash_query(normalized_query)
            table_names = self._extract_table_names(query_text)
            
            # 실행 계획 분석
            explain_plan = await self._get_explain_plan(query_text)
            
            # 최적화 제안 생성
            optimization_suggestions = await self._generate_optimization_suggestions(
                query_text, explain_plan
            )
            
            slow_query = SlowQuery(
                query_hash=query_hash,
                query_text=query_text,
                execution_time=execution_time,
                timestamp=datetime.now(),
                database_name=self.db_config.get('database', 'unknown'),
                table_names=table_names,
                explain_plan=explain_plan,
                optimization_suggestions=optimization_suggestions
            )
            
            self.slow_queries.append(slow_query)
            
            # 버퍼 크기 제한
            if len(self.slow_queries) > self.max_slow_queries:
                self.slow_queries = self.slow_queries[-self.max_slow_queries:]
            
            # 데이터베이스에 저장
            await self._save_slow_query(slow_query)
            
            # 즉시 알림
            await self._send_slow_query_alert(slow_query)
            
            logger.warning(f"🐌 슬로우 쿼리 감지: {execution_time:.2f}초 - {query_text[:100]}...")
            
        except Exception as e:
            logger.error(f"슬로우 쿼리 처리 오류: {e}")
    
    def _normalize_query(self, query: str) -> str:
        """쿼리 정규화"""
        try:
            # 파싱
            parsed = sqlparse.parse(query)[0]
            
            # 정규화 (값들을 플레이스홀더로 대체)
            def normalize_token(token):
                if token.ttype in (sqlparse.tokens.Number.Integer, 
                                 sqlparse.tokens.Number.Float,
                                 sqlparse.tokens.String.Single,
                                 sqlparse.tokens.String.Double):
                    return '?'
                return str(token)
            
            normalized_tokens = []
            for token in parsed.flatten():
                if not token.is_whitespace:
                    normalized_tokens.append(normalize_token(token))
            
            return ' '.join(normalized_tokens).strip()
            
        except Exception:
            # 파싱 실패시 기본 정규화
            normalized = re.sub(r'\b\d+\b', '?', query)  # 숫자
            normalized = re.sub(r"'[^']*'", '?', normalized)  # 문자열
            normalized = re.sub(r'"[^"]*"', '?', normalized)  # 문자열
            normalized = re.sub(r'\s+', ' ', normalized)  # 공백 정리
            return normalized.strip().lower()
    
    def _hash_query(self, normalized_query: str) -> str:
        """쿼리 해시 생성"""
        return hashlib.md5(normalized_query.encode()).hexdigest()
    
    def _extract_table_names(self, query: str) -> List[str]:
        """쿼리에서 테이블 이름 추출"""
        try:
            parsed = sqlparse.parse(query)[0]
            table_names = []
            
            from_seen = False
            for token in parsed.flatten():
                if token.ttype is Keyword and token.value.upper() in ('FROM', 'JOIN', 'UPDATE', 'INTO'):
                    from_seen = True
                elif from_seen and token.ttype is None and not token.is_whitespace:
                    # 간단한 테이블 이름 추출
                    table_name = str(token).strip('(),').split('.')[1] if '.' in str(token) else str(token).strip('(),')
                    if table_name and not table_name.upper() in ('WHERE', 'ON', 'SET', 'VALUES'):
                        table_names.append(table_name)
                        from_seen = False
            
            return list(set(table_names))  # 중복 제거
            
        except Exception:
            # 기본 패턴 매칭
            patterns = [
                r'FROM\s+(\w+)',
                r'JOIN\s+(\w+)',
                r'UPDATE\s+(\w+)',
                r'INTO\s+(\w+)'
            ]
            
            table_names = []
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                table_names.extend(matches)
            
            return list(set(table_names))
    
    async def _get_explain_plan(self, query: str) -> Optional[Dict[str, Any]]:
        """실행 계획 조회"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 실행
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            cursor.execute(explain_query)
            
            result = cursor.fetchone()
            explain_plan = result[0][0] if result and result[0] else None
            
            conn.close()
            return explain_plan
            
        except Exception as e:
            logger.error(f"실행 계획 조회 오류: {e}")
            return None
    
    async def _generate_optimization_suggestions(self, query: str, 
                                               explain_plan: Optional[Dict[str, Any]]) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        try:
            # 쿼리 패턴 분석
            query_upper = query.upper()
            
            # SELECT * 사용 감지
            if 'SELECT *' in query_upper:
                suggestions.append("SELECT * 대신 필요한 컬럼만 지정하세요")
            
            # LIMIT 없는 큰 결과셋
            if 'LIMIT' not in query_upper and any(keyword in query_upper for keyword in ['SELECT', 'UPDATE', 'DELETE']):
                suggestions.append("큰 결과셋에는 LIMIT을 사용하여 결과를 제한하세요")
            
            # 서브쿼리 감지
            if query_upper.count('SELECT') > 1:
                suggestions.append("서브쿼리를 JOIN으로 대체할 수 있는지 검토하세요")
            
            # OR 연산자 많이 사용
            if query.count(' OR ') > 3:
                suggestions.append("여러 OR 조건을 UNION이나 IN 절로 개선할 수 있습니다")
            
            # 실행 계획 기반 제안
            if explain_plan:
                await self._analyze_explain_plan(explain_plan, suggestions)
            
            # 인덱스 제안
            index_suggestions = await self._suggest_indexes_for_query(query)
            suggestions.extend([f"인덱스 제안: {idx.table_name}({', '.join(idx.column_names)})" 
                              for idx in index_suggestions])
            
        except Exception as e:
            logger.error(f"최적화 제안 생성 오류: {e}")
        
        return suggestions
    
    async def _analyze_explain_plan(self, explain_plan: Dict[str, Any], suggestions: List[str]):
        """실행 계획 분석"""
        try:
            plan = explain_plan.get('Plan', {})
            
            # Sequential Scan 감지
            if plan.get('Node Type') == 'Seq Scan':
                table_name = plan.get('Relation Name', 'unknown')
                suggestions.append(f"테이블 '{table_name}'에 순차 스캔이 발생합니다. 인덱스 추가를 고려하세요")
            
            # 높은 비용
            total_cost = plan.get('Total Cost', 0)
            if total_cost > 1000:
                suggestions.append(f"쿼리 비용이 높습니다 (비용: {total_cost:.0f}). 최적화가 필요합니다")
            
            # 많은 행 처리
            rows = plan.get('Plan Rows', 0)
            if rows > 10000:
                suggestions.append(f"많은 행을 처리합니다 ({rows:,}행). 필터링 조건을 추가하세요")
            
            # Nested Loop Join 감지
            if plan.get('Node Type') == 'Nested Loop':
                suggestions.append("Nested Loop Join이 감지되었습니다. 적절한 인덱스가 있는지 확인하세요")
            
            # Hash Join에서 큰 해시 테이블
            if plan.get('Node Type') == 'Hash Join':
                hash_buckets = plan.get('Hash Buckets', 0)
                if hash_buckets > 100000:
                    suggestions.append("Hash Join에서 큰 해시 테이블이 생성됩니다. 조인 조건을 최적화하세요")
            
            # 재귀적으로 하위 플랜 분석
            for plans in plan.get('Plans', []):
                await self._analyze_explain_plan({'Plan': plans}, suggestions)
                
        except Exception as e:
            logger.error(f"실행 계획 분석 오류: {e}")
    
    async def _suggest_indexes_for_query(self, query: str) -> List[IndexSuggestion]:
        """쿼리에 대한 인덱스 제안"""
        suggestions = []
        
        try:
            # WHERE 절 컬럼 추출
            where_columns = self._extract_where_columns(query)
            
            # ORDER BY 절 컬럼 추출
            order_by_columns = self._extract_order_by_columns(query)
            
            # JOIN 절 컬럼 추출
            join_columns = self._extract_join_columns(query)
            
            # 테이블별로 인덱스 제안
            table_names = self._extract_table_names(query)
            
            for table_name in table_names:
                # WHERE 절 인덱스
                table_where_cols = [col for col in where_columns if col['table'] == table_name]
                if table_where_cols:
                    columns = [col['column'] for col in table_where_cols]
                    suggestion = IndexSuggestion(
                        table_name=table_name,
                        column_names=columns,
                        index_type='btree',
                        estimated_benefit=0.7,
                        current_cost=1000.0,
                        estimated_cost=100.0,
                        justification=f"WHERE 절 조건 최적화: {', '.join(columns)}",
                        query_patterns=[query]
                    )
                    suggestions.append(suggestion)
                
                # ORDER BY 절 인덱스
                table_order_cols = [col for col in order_by_columns if col['table'] == table_name]
                if table_order_cols:
                    columns = [col['column'] for col in table_order_cols]
                    suggestion = IndexSuggestion(
                        table_name=table_name,
                        column_names=columns,
                        index_type='btree',
                        estimated_benefit=0.5,
                        current_cost=800.0,
                        estimated_cost=200.0,
                        justification=f"ORDER BY 절 최적화: {', '.join(columns)}",
                        query_patterns=[query]
                    )
                    suggestions.append(suggestion)
            
        except Exception as e:
            logger.error(f"인덱스 제안 생성 오류: {e}")
        
        return suggestions
    
    def _extract_where_columns(self, query: str) -> List[Dict[str, str]]:
        """WHERE 절에서 컬럼 추출"""
        columns = []
        
        try:
            # WHERE 절 추출
            where_match = re.search(r'WHERE\s+(.+?)(?:ORDER BY|GROUP BY|HAVING|LIMIT|$)', 
                                  query, re.IGNORECASE | re.DOTALL)
            
            if where_match:
                where_clause = where_match.group(1)
                
                # 컬럼 패턴 매칭 (table.column 또는 column)
                column_patterns = re.findall(r'(\w+\.)?(\w+)\s*[=<>!]', where_clause, re.IGNORECASE)
                
                for table_prefix, column in column_patterns:
                    table_name = table_prefix.rstrip('.') if table_prefix else 'unknown'
                    columns.append({'table': table_name, 'column': column})
            
        except Exception as e:
            logger.error(f"WHERE 절 컬럼 추출 오류: {e}")
        
        return columns
    
    def _extract_order_by_columns(self, query: str) -> List[Dict[str, str]]:
        """ORDER BY 절에서 컬럼 추출"""
        columns = []
        
        try:
            order_by_match = re.search(r'ORDER BY\s+(.+?)(?:LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
            
            if order_by_match:
                order_clause = order_by_match.group(1)
                
                # 컬럼 패턴 매칭
                column_patterns = re.findall(r'(\w+\.)?(\w+)', order_clause, re.IGNORECASE)
                
                for table_prefix, column in column_patterns:
                    if column.upper() not in ('ASC', 'DESC'):
                        table_name = table_prefix.rstrip('.') if table_prefix else 'unknown'
                        columns.append({'table': table_name, 'column': column})
            
        except Exception as e:
            logger.error(f"ORDER BY 절 컬럼 추출 오류: {e}")
        
        return columns
    
    def _extract_join_columns(self, query: str) -> List[Dict[str, str]]:
        """JOIN 절에서 컬럼 추출"""
        columns = []
        
        try:
            # JOIN ON 절 추출
            join_patterns = re.findall(r'JOIN\s+\w+\s+ON\s+(.+?)(?:WHERE|JOIN|ORDER BY|GROUP BY|$)', 
                                     query, re.IGNORECASE | re.DOTALL)
            
            for join_condition in join_patterns:
                # 컬럼 패턴 매칭
                column_patterns = re.findall(r'(\w+\.)?(\w+)\s*=\s*(\w+\.)?(\w+)', 
                                           join_condition, re.IGNORECASE)
                
                for match in column_patterns:
                    table1, col1, table2, col2 = match
                    columns.append({'table': table1.rstrip('.') if table1 else 'unknown', 'column': col1})
                    columns.append({'table': table2.rstrip('.') if table2 else 'unknown', 'column': col2})
            
        except Exception as e:
            logger.error(f"JOIN 절 컬럼 추출 오류: {e}")
        
        return columns
    
    async def _analyze_slow_queries(self):
        """슬로우 쿼리 분석"""
        while self.monitoring_enabled:
            try:
                if self.slow_queries:
                    # 빈도별 분석
                    await self._analyze_query_patterns()
                    
                    # 테이블별 분석
                    await self._analyze_table_performance()
                    
                    # 인덱스 제안 통합
                    await self._consolidate_index_suggestions()
                
                await asyncio.sleep(300)  # 5분마다 분석
                
            except Exception as e:
                logger.error(f"슬로우 쿼리 분석 오류: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_query_patterns(self):
        """쿼리 패턴 분석"""
        try:
            # 최근 1시간의 슬로우 쿼리
            recent_queries = [
                sq for sq in self.slow_queries 
                if (datetime.now() - sq.timestamp).total_seconds() < 3600
            ]
            
            if not recent_queries:
                return
            
            # 패턴별 그룹화
            pattern_groups = {}
            for query in recent_queries:
                pattern = self._get_query_pattern(query.query_text)
                if pattern not in pattern_groups:
                    pattern_groups[pattern] = []
                pattern_groups[pattern].append(query)
            
            # 빈도 높은 패턴 분석
            for pattern, queries in pattern_groups.items():
                if len(queries) >= 3:  # 3회 이상 반복
                    avg_time = sum(q.execution_time for q in queries) / len(queries)
                    logger.warning(f"🔄 반복되는 슬로우 쿼리 패턴 감지: {pattern} (평균: {avg_time:.2f}초, {len(queries)}회)")
                    
                    # 우선순위 높은 최적화 제안
                    await self._generate_priority_optimization(pattern, queries)
            
        except Exception as e:
            logger.error(f"쿼리 패턴 분석 오류: {e}")
    
    def _get_query_pattern(self, query: str) -> str:
        """쿼리 패턴 추출"""
        # 테이블 이름과 기본 구조만 남기고 간단화
        pattern = re.sub(r'\b\d+\b', 'N', query)  # 숫자를 N으로
        pattern = re.sub(r"'[^']*'", 'STR', pattern)  # 문자열을 STR로
        pattern = re.sub(r'\s+', ' ', pattern)  # 공백 정리
        return pattern.strip().lower()
    
    async def _generate_priority_optimization(self, pattern: str, queries: List[SlowQuery]):
        """우선순위 최적화 제안"""
        try:
            # 가장 대표적인 쿼리 선택 (가장 느린 것)
            representative_query = max(queries, key=lambda q: q.execution_time)
            
            # 인덱스 제안 생성
            index_suggestions = await self._suggest_indexes_for_query(representative_query.query_text)
            
            for suggestion in index_suggestions:
                # 기존 제안과 중복 체크
                existing = any(
                    idx.table_name == suggestion.table_name and 
                    set(idx.column_names) == set(suggestion.column_names)
                    for idx in self.index_suggestions
                )
                
                if not existing:
                    # 빈도 가중치 적용
                    suggestion.estimated_benefit *= min(len(queries) / 3.0, 2.0)
                    self.index_suggestions.append(suggestion)
                    
                    await self._save_index_suggestion(suggestion)
                    logger.info(f"💡 우선순위 인덱스 제안: {suggestion.table_name}({', '.join(suggestion.column_names)})")
            
        except Exception as e:
            logger.error(f"우선순위 최적화 제안 오류: {e}")
    
    async def _analyze_table_performance(self):
        """테이블별 성능 분석"""
        try:
            # 테이블별 슬로우 쿼리 통계
            table_stats = {}
            
            for query in self.slow_queries:
                for table_name in query.table_names:
                    if table_name not in table_stats:
                        table_stats[table_name] = {
                            'count': 0,
                            'total_time': 0.0,
                            'queries': []
                        }
                    
                    table_stats[table_name]['count'] += 1
                    table_stats[table_name]['total_time'] += query.execution_time
                    table_stats[table_name]['queries'].append(query)
            
            # 문제가 많은 테이블 식별
            for table_name, stats in table_stats.items():
                avg_time = stats['total_time'] / stats['count']
                
                if stats['count'] >= 5 and avg_time > 2.0:  # 5회 이상, 평균 2초 이상
                    logger.warning(f"🎯 성능 문제 테이블: {table_name} (평균: {avg_time:.2f}초, {stats['count']}회)")
                    
                    # 테이블별 최적화 제안
                    await self._generate_table_optimization(table_name, stats['queries'])
            
        except Exception as e:
            logger.error(f"테이블별 성능 분석 오류: {e}")
    
    async def _generate_table_optimization(self, table_name: str, queries: List[SlowQuery]):
        """테이블별 최적화 제안"""
        try:
            # 가장 빈번한 컬럼들 분석
            column_frequency = {}
            
            for query in queries:
                where_columns = self._extract_where_columns(query.query_text)
                for col_info in where_columns:
                    if col_info['table'] == table_name or col_info['table'] == 'unknown':
                        column = col_info['column']
                        column_frequency[column] = column_frequency.get(column, 0) + 1
            
            # 빈도 높은 컬럼들로 복합 인덱스 제안
            if column_frequency:
                sorted_columns = sorted(column_frequency.items(), key=lambda x: x[1], reverse=True)
                top_columns = [col for col, freq in sorted_columns[:3] if freq >= 2]  # 상위 3개, 2회 이상
                
                if len(top_columns) > 1:
                    suggestion = IndexSuggestion(
                        table_name=table_name,
                        column_names=top_columns,
                        index_type='btree',
                        estimated_benefit=0.8,
                        current_cost=2000.0,
                        estimated_cost=300.0,
                        justification=f"테이블 '{table_name}' 복합 인덱스로 성능 개선",
                        query_patterns=[q.query_text for q in queries[:3]]
                    )
                    
                    self.index_suggestions.append(suggestion)
                    await self._save_index_suggestion(suggestion)
                    logger.info(f"🔧 테이블 최적화 제안: {table_name}({', '.join(top_columns)})")
            
        except Exception as e:
            logger.error(f"테이블별 최적화 제안 오류: {e}")
    
    async def _generate_index_suggestions(self):
        """인덱스 제안 생성"""
        while self.monitoring_enabled:
            try:
                # 통계 정보 기반 인덱스 제안
                await self._analyze_database_statistics()
                
                # 기존 인덱스 효율성 분석
                await self._analyze_existing_indexes()
                
                await asyncio.sleep(1800)  # 30분마다 실행
                
            except Exception as e:
                logger.error(f"인덱스 제안 생성 오류: {e}")
                await asyncio.sleep(1800)
    
    async def _analyze_database_statistics(self):
        """데이터베이스 통계 분석"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 테이블 통계 조회
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    idx_tup_fetch
                FROM pg_stat_user_tables
                ORDER BY seq_scan DESC
            """)
            
            table_stats = cursor.fetchall()
            
            for stats in table_stats:
                schema, table, inserts, updates, deletes, seq_scans, seq_reads, idx_scans, idx_fetches = stats
                
                # 순차 스캔이 많은 테이블
                if seq_scans > 100 and (idx_scans is None or seq_scans > idx_scans * 2):
                    logger.warning(f"🔍 순차 스캔 과다 테이블: {table} (순차: {seq_scans}, 인덱스: {idx_scans or 0})")
                    
                    # 해당 테이블의 쿼리 패턴 분석
                    await self._suggest_indexes_for_table(table)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"데이터베이스 통계 분석 오류: {e}")
    
    async def _suggest_indexes_for_table(self, table_name: str):
        """특정 테이블에 대한 인덱스 제안"""
        try:
            # 해당 테이블을 사용하는 슬로우 쿼리들 찾기
            table_queries = [
                sq for sq in self.slow_queries 
                if table_name in sq.table_names
            ]
            
            if not table_queries:
                return
            
            # 공통적으로 사용되는 컬럼들 분석
            column_usage = {}
            
            for query in table_queries:
                where_columns = self._extract_where_columns(query.query_text)
                for col_info in where_columns:
                    if col_info['table'] == table_name or col_info['table'] == 'unknown':
                        column = col_info['column']
                        column_usage[column] = column_usage.get(column, 0) + 1
            
            # 사용 빈도 높은 컬럼들로 인덱스 제안
            if column_usage:
                for column, usage_count in column_usage.items():
                    if usage_count >= 2:  # 2회 이상 사용
                        suggestion = IndexSuggestion(
                            table_name=table_name,
                            column_names=[column],
                            index_type='btree',
                            estimated_benefit=min(usage_count * 0.2, 0.9),
                            current_cost=1000.0,
                            estimated_cost=200.0,
                            justification=f"빈번한 WHERE 조건: {column} ({usage_count}회 사용)",
                            query_patterns=[q.query_text for q in table_queries if column in q.query_text]
                        )
                        
                        # 중복 확인 후 추가
                        if not any(idx.table_name == table_name and column in idx.column_names 
                                 for idx in self.index_suggestions):
                            self.index_suggestions.append(suggestion)
                            await self._save_index_suggestion(suggestion)
            
        except Exception as e:
            logger.error(f"테이블 인덱스 제안 오류: {e}")
    
    async def _analyze_existing_indexes(self):
        """기존 인덱스 효율성 분석"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 인덱스 사용 통계 조회
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan ASC
            """)
            
            index_stats = cursor.fetchall()
            
            for stats in index_stats:
                schema, table, index_name, scans, tup_read, tup_fetch = stats
                
                # 사용되지 않는 인덱스
                if scans == 0 or scans < 10:
                    logger.warning(f"🗑️ 미사용 인덱스: {table}.{index_name} (스캔: {scans})")
                    # 실제 환경에서는 DROP INDEX 제안을 신중하게 해야 함
            
            conn.close()
            
        except Exception as e:
            logger.error(f"기존 인덱스 분석 오류: {e}")
    
    async def _consolidate_index_suggestions(self):
        """인덱스 제안 통합"""
        try:
            # 유사한 제안들 통합
            consolidated = {}
            
            for suggestion in self.index_suggestions:
                key = f"{suggestion.table_name}:{':'.join(sorted(suggestion.column_names))}"
                
                if key in consolidated:
                    # 기존 제안과 통합 (더 높은 benefit 사용)
                    existing = consolidated[key]
                    if suggestion.estimated_benefit > existing.estimated_benefit:
                        consolidated[key] = suggestion
                else:
                    consolidated[key] = suggestion
            
            # 통합된 제안으로 교체
            self.index_suggestions = list(consolidated.values())
            
            # 상위 제안들만 유지 (최대 20개)
            self.index_suggestions.sort(key=lambda x: x.estimated_benefit, reverse=True)
            self.index_suggestions = self.index_suggestions[:20]
            
        except Exception as e:
            logger.error(f"인덱스 제안 통합 오류: {e}")
    
    async def _auto_optimize(self):
        """자동 최적화 실행"""
        while self.monitoring_enabled and self.auto_optimize:
            try:
                # 높은 우선순위 인덱스 자동 생성
                await self._auto_create_indexes()
                
                # 자동 통계 업데이트
                await self._auto_update_statistics()
                
                await asyncio.sleep(3600)  # 1시간마다 실행
                
            except Exception as e:
                logger.error(f"자동 최적화 오류: {e}")
                await asyncio.sleep(3600)
    
    async def _auto_create_indexes(self):
        """자동 인덱스 생성"""
        try:
            # 높은 효과가 예상되는 인덱스만 자동 생성
            high_priority_suggestions = [
                idx for idx in self.index_suggestions 
                if idx.estimated_benefit > 0.8 and len(idx.query_patterns) >= 3
            ]
            
            for suggestion in high_priority_suggestions[:3]:  # 최대 3개까지
                success = await self._create_index(suggestion)
                if success:
                    await self._record_optimization_result("index_creation", suggestion)
                    logger.info(f"✅ 자동 인덱스 생성: {suggestion.table_name}({', '.join(suggestion.column_names)})")
            
        except Exception as e:
            logger.error(f"자동 인덱스 생성 오류: {e}")
    
    async def _create_index(self, suggestion: IndexSuggestion) -> bool:
        """인덱스 생성"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # 인덱스 이름 생성
            index_name = f"idx_{suggestion.table_name}_{'_'.join(suggestion.column_names)}"
            
            # 기존 인덱스 확인
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                )
            """, (index_name,))
            
            if cursor.fetchone()[0]:
                logger.info(f"인덱스가 이미 존재합니다: {index_name}")
                return False
            
            # 인덱스 생성 SQL
            columns_str = ', '.join(suggestion.column_names)
            create_sql = f"""
                CREATE INDEX CONCURRENTLY {index_name} 
                ON {suggestion.table_name} ({columns_str})
            """
            
            # 인덱스 생성 (CONCURRENTLY로 락 최소화)
            cursor.execute(create_sql)
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"인덱스 생성 실패 {suggestion.table_name}: {e}")
            return False
    
    async def _auto_update_statistics(self):
        """자동 통계 업데이트"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 통계가 오래된 테이블들 찾기
            cursor.execute("""
                SELECT schemaname, tablename, last_analyze
                FROM pg_stat_user_tables
                WHERE last_analyze < NOW() - INTERVAL '1 day'
                OR last_analyze IS NULL
                ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC
                LIMIT 10
            """)
            
            stale_tables = cursor.fetchall()
            
            for schema, table, last_analyze in stale_tables:
                try:
                    cursor.execute(f"ANALYZE {table}")
                    logger.info(f"📊 통계 업데이트 완료: {table}")
                except Exception as e:
                    logger.error(f"통계 업데이트 실패 {table}: {e}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"자동 통계 업데이트 오류: {e}")
    
    async def _maintenance_tasks(self):
        """유지보수 작업"""
        while self.monitoring_enabled:
            try:
                # 주기적 VACUUM
                await self._auto_vacuum()
                
                # 오래된 데이터 정리
                await self._cleanup_old_data()
                
                # 통계 저장
                await self._save_statistics()
                
                await asyncio.sleep(21600)  # 6시간마다 실행
                
            except Exception as e:
                logger.error(f"유지보수 작업 오류: {e}")
                await asyncio.sleep(21600)
    
    async def _auto_vacuum(self):
        """자동 VACUUM"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # VACUUM이 필요한 테이블들 찾기
            cursor.execute("""
                SELECT schemaname, tablename, n_dead_tup, n_live_tup
                FROM pg_stat_user_tables
                WHERE n_dead_tup > 1000 
                AND n_dead_tup > n_live_tup * 0.1
                ORDER BY n_dead_tup DESC
                LIMIT 5
            """)
            
            vacuum_candidates = cursor.fetchall()
            
            for schema, table, dead_tup, live_tup in vacuum_candidates:
                try:
                    cursor.execute(f"VACUUM ANALYZE {table}")
                    logger.info(f"🧹 VACUUM 완료: {table} (dead: {dead_tup}, live: {live_tup})")
                except Exception as e:
                    logger.error(f"VACUUM 실패 {table}: {e}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"자동 VACUUM 오류: {e}")
    
    async def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            # 7일 이상 된 슬로우 쿼리 삭제
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("DELETE FROM slow_queries WHERE timestamp < ?", (week_ago,))
            
            # 30일 이상 된 최적화 결과 삭제
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute("DELETE FROM optimization_results WHERE execution_time < ?", (month_ago,))
            
            conn.commit()
            conn.close()
            
            # 메모리 데이터도 정리
            cutoff_time = datetime.now() - timedelta(days=1)
            self.slow_queries = [sq for sq in self.slow_queries if sq.timestamp > cutoff_time]
            
        except Exception as e:
            logger.error(f"데이터 정리 오류: {e}")
    
    # 저장 관련 메서드들
    async def _save_slow_query(self, slow_query: SlowQuery):
        """슬로우 쿼리 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO slow_queries 
                (query_hash, query_text, execution_time, timestamp, database_name,
                 table_names, explain_plan, optimization_suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slow_query.query_hash,
                slow_query.query_text,
                slow_query.execution_time,
                slow_query.timestamp.isoformat(),
                slow_query.database_name,
                json.dumps(slow_query.table_names),
                json.dumps(slow_query.explain_plan) if slow_query.explain_plan else None,
                json.dumps(slow_query.optimization_suggestions)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"슬로우 쿼리 저장 오류: {e}")
    
    async def _save_index_suggestion(self, suggestion: IndexSuggestion):
        """인덱스 제안 저장"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO index_suggestions 
                (table_name, column_names, index_type, estimated_benefit,
                 current_cost, estimated_cost, justification, query_patterns, created_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                suggestion.table_name,
                json.dumps(suggestion.column_names),
                suggestion.index_type,
                suggestion.estimated_benefit,
                suggestion.current_cost,
                suggestion.estimated_cost,
                suggestion.justification,
                json.dumps(suggestion.query_patterns),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"인덱스 제안 저장 오류: {e}")
    
    async def _record_optimization_result(self, optimization_type: str, suggestion: IndexSuggestion):
        """최적화 결과 기록"""
        try:
            optimization_id = f"{optimization_type}_{int(time.time())}"
            
            result = OptimizationResult(
                optimization_id=optimization_id,
                optimization_type=optimization_type,
                target_query=f"{suggestion.table_name}({', '.join(suggestion.column_names)})",
                action_taken=f"인덱스 생성: {suggestion.index_type}",
                before_metrics={"cost": suggestion.current_cost},
                after_metrics={"cost": suggestion.estimated_cost},
                improvement_percentage=((suggestion.current_cost - suggestion.estimated_cost) / suggestion.current_cost) * 100,
                execution_time=datetime.now(),
                success=True
            )
            
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO optimization_results 
                (optimization_id, optimization_type, target_query, action_taken,
                 before_metrics, after_metrics, improvement_percentage, execution_time, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.optimization_id,
                result.optimization_type,
                result.target_query,
                result.action_taken,
                json.dumps(result.before_metrics),
                json.dumps(result.after_metrics),
                result.improvement_percentage,
                result.execution_time.isoformat(),
                result.success
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"최적화 결과 기록 오류: {e}")
    
    async def _save_statistics(self):
        """통계 저장"""
        try:
            # 쿼리 통계 저장
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            for query_hash, stats in self.query_stats.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO query_stats 
                    (query_hash, query_text, normalized_query, execution_count,
                     total_time, avg_time, min_time, max_time, rows_examined,
                     rows_returned, first_seen, last_seen, database_name, table_names)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stats.query_hash,
                    stats.query_text,
                    stats.normalized_query,
                    stats.execution_count,
                    stats.total_time,
                    stats.avg_time,
                    stats.min_time,
                    stats.max_time,
                    stats.rows_examined,
                    stats.rows_returned,
                    stats.first_seen.isoformat(),
                    stats.last_seen.isoformat(),
                    stats.database_name,
                    json.dumps(stats.table_names)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"통계 저장 오류: {e}")
    
    async def _update_query_statistics(self):
        """쿼리 통계 업데이트"""
        try:
            # Redis에 캐시된 통계 정보 업데이트
            stats_summary = {
                "total_queries": len(self.query_stats),
                "slow_queries_count": len(self.slow_queries),
                "index_suggestions_count": len(self.index_suggestions),
                "avg_query_time": sum(s.avg_time for s in self.query_stats.values()) / len(self.query_stats) if self.query_stats else 0,
                "last_updated": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                "query_optimizer_stats",
                300,  # 5분 TTL
                json.dumps(stats_summary)
            )
            
        except Exception as e:
            logger.error(f"통계 업데이트 오류: {e}")
    
    async def _send_slow_query_alert(self, slow_query: SlowQuery):
        """슬로우 쿼리 알림"""
        try:
            alert_data = {
                "type": "slow_query_alert",
                "query_hash": slow_query.query_hash,
                "execution_time": slow_query.execution_time,
                "table_names": slow_query.table_names,
                "suggestions": slow_query.optimization_suggestions,
                "timestamp": slow_query.timestamp.isoformat()
            }
            
            # Redis pub/sub로 알림
            self.redis_client.publish("slow_query_alerts", json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"슬로우 쿼리 알림 오류: {e}")
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """최적화 보고서 생성"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            # 최근 24시간 통계
            day_ago = (datetime.now() - timedelta(days=1)).isoformat()
            
            cursor.execute("SELECT COUNT(*) FROM slow_queries WHERE timestamp > ?", (day_ago,))
            recent_slow_queries = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM index_suggestions WHERE created_timestamp > ?", (day_ago,))
            recent_suggestions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM optimization_results WHERE execution_time > ? AND success = 1", (day_ago,))
            recent_optimizations = cursor.fetchone()[0]
            
            # 상위 슬로우 쿼리
            cursor.execute("""
                SELECT query_text, execution_time, table_names
                FROM slow_queries 
                WHERE timestamp > ?
                ORDER BY execution_time DESC 
                LIMIT 10
            """, (day_ago,))
            top_slow_queries = cursor.fetchall()
            
            # 최적화 효과
            cursor.execute("""
                SELECT AVG(improvement_percentage)
                FROM optimization_results 
                WHERE execution_time > ? AND success = 1
            """, (day_ago,))
            avg_improvement = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "report_time": datetime.now().isoformat(),
                "recent_slow_queries": recent_slow_queries,
                "recent_suggestions": recent_suggestions,
                "recent_optimizations": recent_optimizations,
                "average_improvement": avg_improvement,
                "top_slow_queries": [
                    {
                        "query": query[:200] + "..." if len(query) > 200 else query,
                        "execution_time": exec_time,
                        "tables": json.loads(tables) if tables else []
                    }
                    for query, exec_time, tables in top_slow_queries
                ],
                "current_suggestions": len(self.index_suggestions),
                "monitoring_status": "active" if self.monitoring_enabled else "inactive"
            }
            
        except Exception as e:
            logger.error(f"최적화 보고서 생성 오류: {e}")
            return {}

# 메인 실행
async def main():
    """메인 실행 함수"""
    # 데이터베이스 설정 (환경변수나 설정 파일에서 로드)
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'yourprogram',
        'user': 'postgres',
        'password': 'your_password'
    }
    
    optimizer = DatabaseQueryOptimizer(db_config)
    
    try:
        logger.info("🗄️ 데이터베이스 쿼리 최적화 시스템 시작")
        await optimizer.start_monitoring()
    except KeyboardInterrupt:
        logger.info("⏹️ 시스템 종료")
        optimizer.monitoring_enabled = False
    except Exception as e:
        logger.error(f"시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 