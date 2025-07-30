"""
데이터 웨어하우스 관리자
엔터프라이즈급 데이터 웨어하우스 시스템
"""

import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableType(Enum):
    """테이블 타입"""
    DIMENSION = "dimension"
    FACT = "fact"
    AGGREGATE = "aggregate"
    STAGING = "staging"

class DataGranularity(Enum):
    """데이터 세분성"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class TableSchema:
    """테이블 스키마"""
    name: str
    table_type: TableType
    columns: List[Dict[str, Any]]
    primary_key: List[str]
    foreign_keys: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    partitions: Optional[List[str]] = None
    retention_days: Optional[int] = None

@dataclass
class DataLoadJob:
    """데이터 로드 작업"""
    id: str
    table_name: str
    source_type: str
    source_config: Dict[str, Any]
    load_type: str  # full, incremental, delta
    status: str  # pending, running, completed, failed
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None

class DataWarehouseManager:
    """데이터 웨어하우스 관리자"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self.metadata = MetaData()
        self.Base = declarative_base()
        self.tables: Dict[str, TableSchema] = {}
        self.load_jobs: Dict[str, DataLoadJob] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self._initialize_connections()
        self._load_table_schemas()
        self._create_tables()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # PostgreSQL 연결
            connection_string = (
                f"postgresql://{self.config['database']['user']}:"
                f"{self.config['database']['password']}@"
                f"{self.config['database']['host']}:"
                f"{self.config['database']['port']}/"
                f"{self.config['database']['name']}"
            )
            
            self.engine = create_engine(connection_string, pool_size=10, max_overflow=20)
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            logger.info("데이터 웨어하우스 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _load_table_schemas(self):
        """테이블 스키마 로드"""
        try:
            # 기본 스키마 정의
            self.tables = {
                # 차원 테이블들
                'dim_users': TableSchema(
                    name='dim_users',
                    table_type=TableType.DIMENSION,
                    columns=[
                        {'name': 'user_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'username', 'type': 'VARCHAR(100)', 'nullable': False},
                        {'name': 'email', 'type': 'VARCHAR(255)', 'nullable': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False},
                        {'name': 'updated_at', 'type': 'TIMESTAMP', 'nullable': False},
                        {'name': 'is_active', 'type': 'BOOLEAN', 'nullable': False, 'default': True}
                    ],
                    primary_key=['user_id'],
                    foreign_keys=[],
                    indexes=[
                        {'name': 'idx_dim_users_username', 'columns': ['username']},
                        {'name': 'idx_dim_users_email', 'columns': ['email']}
                    ]
                ),
                
                'dim_products': TableSchema(
                    name='dim_products',
                    table_type=TableType.DIMENSION,
                    columns=[
                        {'name': 'product_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'product_name', 'type': 'VARCHAR(255)', 'nullable': False},
                        {'name': 'category', 'type': 'VARCHAR(100)', 'nullable': True},
                        {'name': 'price', 'type': 'DECIMAL(10,2)', 'nullable': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False},
                        {'name': 'updated_at', 'type': 'TIMESTAMP', 'nullable': False}
                    ],
                    primary_key=['product_id'],
                    foreign_keys=[],
                    indexes=[
                        {'name': 'idx_dim_products_category', 'columns': ['category']},
                        {'name': 'idx_dim_products_price', 'columns': ['price']}
                    ]
                ),
                
                'dim_time': TableSchema(
                    name='dim_time',
                    table_type=TableType.DIMENSION,
                    columns=[
                        {'name': 'time_id', 'type': 'VARCHAR(20)', 'nullable': False},
                        {'name': 'date', 'type': 'DATE', 'nullable': False},
                        {'name': 'year', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'month', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'day', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'quarter', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'week_of_year', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'day_of_week', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'is_weekend', 'type': 'BOOLEAN', 'nullable': False},
                        {'name': 'is_holiday', 'type': 'BOOLEAN', 'nullable': False}
                    ],
                    primary_key=['time_id'],
                    foreign_keys=[],
                    indexes=[
                        {'name': 'idx_dim_time_date', 'columns': ['date']},
                        {'name': 'idx_dim_time_year_month', 'columns': ['year', 'month']}
                    ]
                ),
                
                # 팩트 테이블들
                'fact_user_activity': TableSchema(
                    name='fact_user_activity',
                    table_type=TableType.FACT,
                    columns=[
                        {'name': 'activity_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'user_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'time_id', 'type': 'VARCHAR(20)', 'nullable': False},
                        {'name': 'activity_type', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'session_duration', 'type': 'INTEGER', 'nullable': True},
                        {'name': 'page_views', 'type': 'INTEGER', 'nullable': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False}
                    ],
                    primary_key=['activity_id'],
                    foreign_keys=[
                        {'column': 'user_id', 'references': 'dim_users(user_id)'},
                        {'column': 'time_id', 'references': 'dim_time(time_id)'}
                    ],
                    indexes=[
                        {'name': 'idx_fact_user_activity_user_time', 'columns': ['user_id', 'time_id']},
                        {'name': 'idx_fact_user_activity_type', 'columns': ['activity_type']}
                    ],
                    partitions=['time_id'],
                    retention_days=365
                ),
                
                'fact_sales': TableSchema(
                    name='fact_sales',
                    table_type=TableType.FACT,
                    columns=[
                        {'name': 'sale_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'user_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'product_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'time_id', 'type': 'VARCHAR(20)', 'nullable': False},
                        {'name': 'quantity', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'unit_price', 'type': 'DECIMAL(10,2)', 'nullable': False},
                        {'name': 'total_amount', 'type': 'DECIMAL(12,2)', 'nullable': False},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False}
                    ],
                    primary_key=['sale_id'],
                    foreign_keys=[
                        {'column': 'user_id', 'references': 'dim_users(user_id)'},
                        {'column': 'product_id', 'references': 'dim_products(product_id)'},
                        {'column': 'time_id', 'references': 'dim_time(time_id)'}
                    ],
                    indexes=[
                        {'name': 'idx_fact_sales_user_time', 'columns': ['user_id', 'time_id']},
                        {'name': 'idx_fact_sales_product_time', 'columns': ['product_id', 'time_id']},
                        {'name': 'idx_fact_sales_amount', 'columns': ['total_amount']}
                    ],
                    partitions=['time_id'],
                    retention_days=730
                ),
                
                # 집계 테이블들
                'agg_daily_sales': TableSchema(
                    name='agg_daily_sales',
                    table_type=TableType.AGGREGATE,
                    columns=[
                        {'name': 'time_id', 'type': 'VARCHAR(20)', 'nullable': False},
                        {'name': 'total_sales', 'type': 'DECIMAL(15,2)', 'nullable': False},
                        {'name': 'total_orders', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'unique_customers', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'avg_order_value', 'type': 'DECIMAL(10,2)', 'nullable': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False},
                        {'name': 'updated_at', 'type': 'TIMESTAMP', 'nullable': False}
                    ],
                    primary_key=['time_id'],
                    foreign_keys=[
                        {'column': 'time_id', 'references': 'dim_time(time_id)'}
                    ],
                    indexes=[
                        {'name': 'idx_agg_daily_sales_time', 'columns': ['time_id']}
                    ]
                ),
                
                'agg_user_behavior': TableSchema(
                    name='agg_user_behavior',
                    table_type=TableType.AGGREGATE,
                    columns=[
                        {'name': 'user_id', 'type': 'VARCHAR(50)', 'nullable': False},
                        {'name': 'time_id', 'type': 'VARCHAR(20)', 'nullable': False},
                        {'name': 'total_sessions', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'total_duration', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'total_page_views', 'type': 'INTEGER', 'nullable': False},
                        {'name': 'avg_session_duration', 'type': 'DECIMAL(8,2)', 'nullable': True},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False},
                        {'name': 'updated_at', 'type': 'TIMESTAMP', 'nullable': False}
                    ],
                    primary_key=['user_id', 'time_id'],
                    foreign_keys=[
                        {'column': 'user_id', 'references': 'dim_users(user_id)'},
                        {'column': 'time_id', 'references': 'dim_time(time_id)'}
                    ],
                    indexes=[
                        {'name': 'idx_agg_user_behavior_user_time', 'columns': ['user_id', 'time_id']}
                    ]
                )
            }
            
            logger.info(f"{len(self.tables)}개의 테이블 스키마 로드 완료")
            
        except Exception as e:
            logger.error(f"테이블 스키마 로드 오류: {e}")
            raise
    
    def _create_tables(self):
        """테이블 생성"""
        try:
            with self.engine.connect() as connection:
                for table_name, schema in self.tables.items():
                    self._create_table(connection, schema)
            
            logger.info("모든 테이블 생성 완료")
            
        except Exception as e:
            logger.error(f"테이블 생성 오류: {e}")
            raise
    
    def _create_table(self, connection, schema: TableSchema):
        """개별 테이블 생성"""
        try:
            # 컬럼 정의 생성
            columns = []
            for col in schema.columns:
                col_def = f"{col['name']} {col['type']}"
                if not col.get('nullable', True):
                    col_def += " NOT NULL"
                if 'default' in col:
                    col_def += f" DEFAULT {col['default']}"
                columns.append(col_def)
            
            # 기본키 정의
            primary_key = f"PRIMARY KEY ({', '.join(schema.primary_key)})"
            
            # 외래키 정의
            foreign_keys = []
            for fk in schema.foreign_keys:
                fk_def = f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']}"
                foreign_keys.append(fk_def)
            
            # 인덱스 정의
            indexes = []
            for idx in schema.indexes:
                idx_def = f"CREATE INDEX {idx['name']} ON {schema.name} ({', '.join(idx['columns'])})"
                indexes.append(idx_def)
            
            # 테이블 생성 SQL
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema.name} (
                {', '.join(columns)},
                {primary_key}
                {', ' + ', '.join(foreign_keys) if foreign_keys else ''}
            )
            """
            
            # 테이블 생성
            connection.execute(text(create_sql))
            
            # 인덱스 생성
            for idx_sql in indexes:
                try:
                    connection.execute(text(idx_sql))
                except Exception as e:
                    logger.warning(f"인덱스 생성 실패 ({idx['name']}): {e}")
            
            logger.info(f"테이블 생성 완료: {schema.name}")
            
        except Exception as e:
            logger.error(f"테이블 생성 오류 ({schema.name}): {e}")
            raise
    
    def load_data(self, table_name: str, data: List[Dict[str, Any]], 
                  load_type: str = 'incremental') -> str:
        """데이터 로드"""
        try:
            job_id = str(uuid.uuid4())
            
            # 로드 작업 생성
            job = DataLoadJob(
                id=job_id,
                table_name=table_name,
                source_type='dataframe',
                source_config={'records_count': len(data)},
                load_type=load_type,
                status='pending',
                created_at=datetime.now()
            )
            
            self.load_jobs[job_id] = job
            
            # 비동기로 데이터 로드 실행
            self.executor.submit(self._execute_data_load, job_id, data)
            
            logger.info(f"데이터 로드 작업 시작: {job_id} ({table_name})")
            return job_id
            
        except Exception as e:
            logger.error(f"데이터 로드 오류: {e}")
            raise
    
    def _execute_data_load(self, job_id: str, data: List[Dict[str, Any]]):
        """데이터 로드 실행"""
        job = self.load_jobs[job_id]
        
        try:
            job.status = 'running'
            job.started_at = datetime.now()
            
            # 데이터프레임 생성
            df = pd.DataFrame(data)
            
            # 데이터 검증
            validated_data = self._validate_data(df, job.table_name)
            
            # 데이터 로드
            if job.load_type == 'full':
                self._load_full_data(job.table_name, validated_data)
            elif job.load_type == 'incremental':
                self._load_incremental_data(job.table_name, validated_data)
            elif job.load_type == 'delta':
                self._load_delta_data(job.table_name, validated_data)
            
            job.status = 'completed'
            job.completed_at = datetime.now()
            job.records_processed = len(validated_data)
            
            # 집계 테이블 업데이트
            self._update_aggregate_tables(job.table_name)
            
            logger.info(f"데이터 로드 완료: {job_id} ({job.records_processed} 레코드)")
            
        except Exception as e:
            job.status = 'failed'
            job.completed_at = datetime.now()
            job.error_message = str(e)
            job.records_failed = len(data)
            
            logger.error(f"데이터 로드 실패: {job_id} - {e}")
    
    def _validate_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """데이터 검증"""
        try:
            schema = self.tables[table_name]
            
            # 필수 컬럼 확인
            required_columns = [col['name'] for col in schema.columns if not col.get('nullable', True)]
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                raise ValueError(f"필수 컬럼 누락: {missing_columns}")
            
            # 데이터 타입 변환
            for col in schema.columns:
                if col['name'] in df.columns:
                    if col['type'].startswith('TIMESTAMP'):
                        df[col['name']] = pd.to_datetime(df[col['name']])
                    elif col['type'].startswith('DECIMAL'):
                        df[col['name']] = pd.to_numeric(df[col['name']], errors='coerce')
                    elif col['type'] == 'BOOLEAN':
                        df[col['name']] = df[col['name']].astype(bool)
            
            # NULL 값 처리
            for col in schema.columns:
                if col['name'] in df.columns and not col.get('nullable', True):
                    df[col['name']] = df[col['name']].fillna(col.get('default', ''))
            
            return df
            
        except Exception as e:
            logger.error(f"데이터 검증 오류: {e}")
            raise
    
    def _load_full_data(self, table_name: str, df: pd.DataFrame):
        """전체 데이터 로드"""
        try:
            with self.engine.connect() as connection:
                # 기존 데이터 삭제
                connection.execute(text(f"DELETE FROM {table_name}"))
                
                # 새 데이터 삽입
                df.to_sql(table_name, connection, if_exists='append', index=False)
                connection.commit()
                
        except Exception as e:
            logger.error(f"전체 데이터 로드 오류: {e}")
            raise
    
    def _load_incremental_data(self, table_name: str, df: pd.DataFrame):
        """증분 데이터 로드"""
        try:
            with self.engine.connect() as connection:
                # 중복 데이터 제거
                if 'updated_at' in df.columns:
                    # updated_at 기준으로 최신 데이터만 유지
                    df = df.sort_values('updated_at').drop_duplicates(
                        subset=[col for col in df.columns if col != 'updated_at'],
                        keep='last'
                    )
                
                # 데이터 삽입
                df.to_sql(table_name, connection, if_exists='append', index=False)
                connection.commit()
                
        except Exception as e:
            logger.error(f"증분 데이터 로드 오류: {e}")
            raise
    
    def _load_delta_data(self, table_name: str, df: pd.DataFrame):
        """델타 데이터 로드"""
        try:
            with self.engine.connect() as connection:
                # 변경된 데이터만 업데이트
                for _, row in df.iterrows():
                    # UPSERT 로직 (PostgreSQL의 ON CONFLICT 사용)
                    columns = list(row.index)
                    values = list(row.values)
                    
                    update_sets = [f"{col} = EXCLUDED.{col}" for col in columns if col != 'id']
                    
                    insert_sql = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({', '.join(['%s'] * len(values))})
                    ON CONFLICT (id) DO UPDATE SET
                    {', '.join(update_sets)}
                    """
                    
                    connection.execute(text(insert_sql), values)
                
                connection.commit()
                
        except Exception as e:
            logger.error(f"델타 데이터 로드 오류: {e}")
            raise
    
    def _update_aggregate_tables(self, source_table: str):
        """집계 테이블 업데이트"""
        try:
            if source_table == 'fact_sales':
                self._update_daily_sales_aggregate()
            elif source_table == 'fact_user_activity':
                self._update_user_behavior_aggregate()
                
        except Exception as e:
            logger.error(f"집계 테이블 업데이트 오류: {e}")
    
    def _update_daily_sales_aggregate(self):
        """일일 매출 집계 업데이트"""
        try:
            with self.engine.connect() as connection:
                # 일일 매출 집계 쿼리
                aggregate_sql = """
                INSERT INTO agg_daily_sales (time_id, total_sales, total_orders, unique_customers, avg_order_value, created_at, updated_at)
                SELECT 
                    time_id,
                    SUM(total_amount) as total_sales,
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT user_id) as unique_customers,
                    AVG(total_amount) as avg_order_value,
                    NOW() as created_at,
                    NOW() as updated_at
                FROM fact_sales
                WHERE time_id NOT IN (SELECT time_id FROM agg_daily_sales)
                GROUP BY time_id
                ON CONFLICT (time_id) DO UPDATE SET
                    total_sales = EXCLUDED.total_sales,
                    total_orders = EXCLUDED.total_orders,
                    unique_customers = EXCLUDED.unique_customers,
                    avg_order_value = EXCLUDED.avg_order_value,
                    updated_at = NOW()
                """
                
                connection.execute(text(aggregate_sql))
                connection.commit()
                
        except Exception as e:
            logger.error(f"일일 매출 집계 업데이트 오류: {e}")
    
    def _update_user_behavior_aggregate(self):
        """사용자 행동 집계 업데이트"""
        try:
            with self.engine.connect() as connection:
                # 사용자 행동 집계 쿼리
                aggregate_sql = """
                INSERT INTO agg_user_behavior (user_id, time_id, total_sessions, total_duration, total_page_views, avg_session_duration, created_at, updated_at)
                SELECT 
                    user_id,
                    time_id,
                    COUNT(*) as total_sessions,
                    SUM(session_duration) as total_duration,
                    SUM(page_views) as total_page_views,
                    AVG(session_duration) as avg_session_duration,
                    NOW() as created_at,
                    NOW() as updated_at
                FROM fact_user_activity
                WHERE (user_id, time_id) NOT IN (SELECT user_id, time_id FROM agg_user_behavior)
                GROUP BY user_id, time_id
                ON CONFLICT (user_id, time_id) DO UPDATE SET
                    total_sessions = EXCLUDED.total_sessions,
                    total_duration = EXCLUDED.total_duration,
                    total_page_views = EXCLUDED.total_page_views,
                    avg_session_duration = EXCLUDED.avg_session_duration,
                    updated_at = NOW()
                """
                
                connection.execute(text(aggregate_sql))
                connection.commit()
                
        except Exception as e:
            logger.error(f"사용자 행동 집계 업데이트 오류: {e}")
    
    def query_data(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """데이터 쿼리"""
        try:
            with self.engine.connect() as connection:
                if params:
                    result = connection.execute(text(sql), params)
                else:
                    result = connection.execute(text(sql))
                
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df
                
        except Exception as e:
            logger.error(f"데이터 쿼리 오류: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """테이블 정보 조회"""
        try:
            schema = self.tables.get(table_name)
            if not schema:
                raise ValueError(f"테이블을 찾을 수 없습니다: {table_name}")
            
            # 테이블 통계 조회
            stats_sql = f"SELECT COUNT(*) as row_count FROM {table_name}"
            row_count = self.query_data(stats_sql).iloc[0]['row_count']
            
            return {
                'name': schema.name,
                'type': schema.table_type.value,
                'columns': schema.columns,
                'primary_key': schema.primary_key,
                'foreign_keys': schema.foreign_keys,
                'indexes': schema.indexes,
                'row_count': row_count,
                'partitions': schema.partitions,
                'retention_days': schema.retention_days
            }
            
        except Exception as e:
            logger.error(f"테이블 정보 조회 오류: {e}")
            raise
    
    def get_load_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """로드 작업 상태 조회"""
        try:
            job = self.load_jobs.get(job_id)
            if not job:
                return None
            
            return asdict(job)
            
        except Exception as e:
            logger.error(f"로드 작업 상태 조회 오류: {e}")
            raise
    
    def cleanup_old_data(self):
        """오래된 데이터 정리"""
        try:
            for table_name, schema in self.tables.items():
                if schema.retention_days:
                    cleanup_sql = f"""
                    DELETE FROM {table_name}
                    WHERE created_at < NOW() - INTERVAL '{schema.retention_days} days'
                    """
                    
                    with self.engine.connect() as connection:
                        result = connection.execute(text(cleanup_sql))
                        connection.commit()
                        
                        logger.info(f"오래된 데이터 정리 완료: {table_name} ({result.rowcount} 레코드)")
                        
        except Exception as e:
            logger.error(f"오래된 데이터 정리 오류: {e}")
    
    def optimize_tables(self):
        """테이블 최적화"""
        try:
            with self.engine.connect() as connection:
                for table_name in self.tables.keys():
                    # VACUUM 및 ANALYZE 실행
                    connection.execute(text(f"VACUUM ANALYZE {table_name}"))
                
                connection.commit()
                logger.info("테이블 최적화 완료")
                
        except Exception as e:
            logger.error(f"테이블 최적화 오류: {e}")
    
    def get_warehouse_stats(self) -> Dict[str, Any]:
        """웨어하우스 통계"""
        try:
            stats = {
                'total_tables': len(self.tables),
                'dimension_tables': len([t for t in self.tables.values() if t.table_type == TableType.DIMENSION]),
                'fact_tables': len([t for t in self.tables.values() if t.table_type == TableType.FACT]),
                'aggregate_tables': len([t for t in self.tables.values() if t.table_type == TableType.AGGREGATE]),
                'total_rows': 0,
                'active_load_jobs': len([j for j in self.load_jobs.values() if j.status == 'running']),
                'failed_load_jobs': len([j for j in self.load_jobs.values() if j.status == 'failed'])
            }
            
            # 전체 행 수 계산
            for table_name in self.tables.keys():
                try:
                    count_sql = f"SELECT COUNT(*) as count FROM {table_name}"
                    count = self.query_data(count_sql).iloc[0]['count']
                    stats['total_rows'] += count
                except Exception as e:
                    logger.warning(f"테이블 행 수 계산 실패 ({table_name}): {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"웨어하우스 통계 조회 오류: {e}")
            raise

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program_warehouse',
            'user': 'postgres',
            'password': 'password'
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 1
        }
    }
    
    # 웨어하우스 매니저 생성
    warehouse = DataWarehouseManager(config)
    
    # 샘플 데이터 로드
    sample_sales_data = [
        {
            'sale_id': 'SALE001',
            'user_id': 'USER001',
            'product_id': 'PROD001',
            'time_id': '20250101',
            'quantity': 2,
            'unit_price': 29.99,
            'total_amount': 59.98,
            'created_at': datetime.now()
        }
    ]
    
    # 데이터 로드
    job_id = warehouse.load_data('fact_sales', sample_sales_data, 'incremental')
    print(f"데이터 로드 작업 시작: {job_id}")
    
    # 웨어하우스 통계
    stats = warehouse.get_warehouse_stats()
    print(f"웨어하우스 통계: {stats}") 