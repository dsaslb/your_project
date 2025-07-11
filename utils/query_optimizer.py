from typing import List, Dict, Any, Optional
from sqlalchemy import and_, func, desc, asc
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime
from functools import wraps
from models import User, Attendance

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """데이터베이스 쿼리 최적화 클래스"""
    
    @staticmethod
    def optimize_user_query(query, include_relations: Optional[List[str]] = None):
        if include_relations is None:
            include_relations = []
        """사용자 쿼리 최적화"""
        if include_relations:
            if 'attendances' in include_relations:
                query = query.options(selectinload(getattr(User, 'attendances')))
            if 'notifications' in include_relations:
                query = query.options(selectinload(getattr(User, 'notifications')))
            if 'branch' in include_relations:
                query = query.options(joinedload(getattr(User, 'branch')))
            if 'brand' in include_relations:
                query = query.options(joinedload(getattr(User, 'brand')))
        
        return query
    
    @staticmethod
    def optimize_attendance_query(query, date_range: Optional[Dict] = None):
        """출퇴근 쿼리 최적화"""
        if date_range:
            start_date = date_range.get('start')
            end_date = date_range.get('end')
            
            if start_date and end_date:
                query = query.filter(
                    and_(
                        func.date(query.column('clock_in')) >= start_date,
                        func.date(query.column('clock_in')) <= end_date
                    )
                )
        
        # 사용자 정보 미리 로드
        query = query.options(joinedload(getattr(Attendance, 'user')))
        
        return query
    
    @staticmethod
    def optimize_schedule_query(query, filters: Optional[Dict] = None):
        """스케줄 쿼리 최적화"""
        if filters:
            if 'user_id' in filters:
                query = query.filter(query.column('user_id') == filters['user_id'])
            if 'date_range' in filters:
                start_date = filters['date_range'].get('start')
                end_date = filters['date_range'].get('end')
                if start_date and end_date:
                    query = query.filter(
                        and_(
                            query.column('date') >= start_date,
                            query.column('date') <= end_date
                        )
                    )
        
        # 사용자 정보 미리 로드
        query = query.options(joinedload(getattr(Attendance, 'user')))
        
        return query
    
    @staticmethod
    def optimize_order_query(query, filters: Optional[Dict] = None):
        """주문 쿼리 최적화"""
        if filters:
            if 'status' in filters:
                query = query.filter(query.column('status') == filters['status'])
            if 'date_range' in filters:
                start_date = filters['date_range'].get('start')
                end_date = filters['date_range'].get('end')
                if start_date and end_date:
                    query = query.filter(
                        and_(
                            query.column('created_at') >= start_date,
                            query.column('created_at') <= end_date
                        )
                    )
        
        return query
    
    @staticmethod
    def optimize_inventory_query(query, filters: Optional[Dict] = None):
        """재고 쿼리 최적화"""
        if filters:
            if 'low_stock' in filters and filters['low_stock']:
                query = query.filter(query.column('quantity') <= query.column('min_quantity'))
            if 'category' in filters:
                query = query.filter(query.column('category') == filters['category'])
        
        return query

def query_performance_monitor(func):
    """쿼리 성능 모니터링 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if execution_time > 1.0:  # 1초 이상 걸리는 쿼리 경고
                logger.warning(f"느린 쿼리 감지: {func.__name__} - {execution_time:.2f}초")
            
            return result
        except SQLAlchemyError as e:
            logger.error(f"쿼리 오류: {func.__name__} - {str(e)}")
            raise
    
    return wrapper

class PaginationHelper:
    """페이지네이션 헬퍼 클래스"""
    
    @staticmethod
    def paginate_query(query, page: int = 1, per_page: int = 20):
        """쿼리 페이지네이션"""
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page)
    
    @staticmethod
    def get_pagination_info(total_count: int, page: int, per_page: int) -> Dict[str, Any]:
        """페이지네이션 정보 생성"""
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            'current_page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }

class QueryBuilder:
    """동적 쿼리 빌더"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.filters = []
        self.orders = []
        self.includes = []
    
    def filter(self, condition):
        """필터 조건 추가"""
        self.filters.append(condition)
        return self
    
    def order_by(self, column, direction='asc'):
        """정렬 조건 추가"""
        if direction.lower() == 'desc':
            self.orders.append(desc(column))
        else:
            self.orders.append(asc(column))
        return self
    
    def include(self, relation):
        """관계 로드 추가"""
        self.includes.append(relation)
        return self
    
    def build(self, session):
        """쿼리 빌드"""
        query = session.query(self.model_class)
        
        # 필터 적용
        if self.filters:
            query = query.filter(and_(*self.filters))
        
        # 정렬 적용
        if self.orders:
            query = query.order_by(*self.orders)
        
        # 관계 로드 적용
        for include in self.includes:
            query = query.options(joinedload(include))
        
        return query

class BulkOperationHelper:
    """대량 작업 헬퍼 클래스"""
    
    @staticmethod
    def bulk_insert(session, model_class, data_list: List[Dict], batch_size: int = 1000):
        """대량 삽입"""
        try:
            total_inserted = 0
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                objects = [model_class(**data) for data in batch]
                session.bulk_save_objects(objects)
                session.commit()
                total_inserted += len(batch)
                logger.info(f"대량 삽입 진행률: {total_inserted}/{len(data_list)}")
            
            return total_inserted
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"대량 삽입 실패: {str(e)}")
            raise
    
    @staticmethod
    def bulk_update(session, model_class, update_data: List[Dict], id_field: str = 'id'):
        """대량 업데이트"""
        try:
            updated_count = 0
            for data in update_data:
                record_id = data.pop(id_field)
                session.query(model_class).filter(
                    getattr(model_class, id_field) == record_id
                ).update(data)
                updated_count += 1
            
            session.commit()
            return updated_count
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"대량 업데이트 실패: {str(e)}")
            raise

class QueryCache:
    """쿼리 결과 캐싱"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def get_cached_query(self, cache_key: str, query_func, ttl: int = 300):
        """캐시된 쿼리 결과 조회"""
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = query_func()
        self.cache_manager.set(cache_key, result, ttl)
        return result
    
    def invalidate_cache_pattern(self, pattern: str):
        """캐시 패턴 무효화"""
        return self.cache_manager.invalidate_pattern(pattern) 