"""
중앙 데이터 레이어
모든 모듈이 공유하는 통합 데이터 관리 시스템
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path
import threading
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataType(Enum):
    """데이터 타입"""
    EMPLOYEE = "employee"
    BRANCH = "branch"
    BRAND = "brand"
    ATTENDANCE = "attendance"
    SALES = "sales"
    PAYROLL = "payroll"
    INVENTORY = "inventory"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"

class CentralDataLayer:
    """중앙 데이터 레이어 - 모든 모듈의 데이터를 통합 관리"""
    
    def __init__(self, db_path: str = "data/central_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._init_database()
        self._load_sample_data()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 브랜드 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS brands (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        industry TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 매장 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS branches (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        brand_id INTEGER,
                        address TEXT,
                        phone TEXT,
                        manager_id INTEGER,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (brand_id) REFERENCES brands (id)
                    )
                ''')
                
                # 직원 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        username TEXT UNIQUE,
                        email TEXT,
                        phone TEXT,
                        position TEXT,
                        department TEXT,
                        branch_id INTEGER,
                        brand_id INTEGER,
                        hourly_wage REAL DEFAULT 0,
                        monthly_salary REAL DEFAULT 0,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (branch_id) REFERENCES branches (id),
                        FOREIGN KEY (brand_id) REFERENCES brands (id)
                    )
                ''')
                
                # 출퇴근 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY,
                        employee_id INTEGER,
                        branch_id INTEGER,
                        date DATE NOT NULL,
                        clock_in TIMESTAMP,
                        clock_out TIMESTAMP,
                        work_hours REAL,
                        is_late BOOLEAN DEFAULT FALSE,
                        is_overtime BOOLEAN DEFAULT FALSE,
                        status TEXT DEFAULT 'checked_in',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees (id),
                        FOREIGN KEY (branch_id) REFERENCES branches (id)
                    )
                ''')
                
                # 매출 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY,
                        branch_id INTEGER,
                        employee_id INTEGER,
                        date DATE NOT NULL,
                        amount REAL NOT NULL,
                        items_count INTEGER DEFAULT 1,
                        category TEXT,
                        payment_method TEXT,
                        status TEXT DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (branch_id) REFERENCES branches (id),
                        FOREIGN KEY (employee_id) REFERENCES employees (id)
                    )
                ''')
                
                # 급여 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payroll (
                        id INTEGER PRIMARY KEY,
                        employee_id INTEGER,
                        branch_id INTEGER,
                        year INTEGER,
                        month INTEGER,
                        base_salary REAL,
                        overtime_pay REAL DEFAULT 0,
                        bonus REAL DEFAULT 0,
                        deduction REAL DEFAULT 0,
                        net_salary REAL,
                        work_hours REAL,
                        attendance_days INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees (id),
                        FOREIGN KEY (branch_id) REFERENCES branches (id)
                    )
                ''')
                
                # 재고 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY,
                        branch_id INTEGER,
                        name TEXT NOT NULL,
                        category TEXT,
                        current_stock INTEGER DEFAULT 0,
                        min_stock INTEGER DEFAULT 0,
                        max_stock INTEGER DEFAULT 0,
                        unit_price REAL DEFAULT 0,
                        supplier TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (branch_id) REFERENCES branches (id)
                    )
                ''')
                
                # 알림 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        title TEXT NOT NULL,
                        message TEXT,
                        type TEXT,
                        priority TEXT DEFAULT 'normal',
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 분석 결과 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY,
                        branch_id INTEGER,
                        analysis_type TEXT,
                        period TEXT,
                        data JSON,
                        insights TEXT,
                        recommendations TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (branch_id) REFERENCES branches (id)
                    )
                ''')
                
                conn.commit()
                logger.info("중앙 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _load_sample_data(self):
        """샘플 데이터 로드"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 브랜드 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM brands")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_brands(cursor)
                
                # 매장 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM branches")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_branches(cursor)
                
                # 직원 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM employees")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_employees(cursor)
                
                # 출퇴근 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM attendance")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_attendance(cursor)
                
                # 매출 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM sales")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_sales(cursor)
                
                # 급여 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM payroll")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_payroll(cursor)
                
                # 재고 데이터 확인
                cursor.execute("SELECT COUNT(*) FROM inventory")
                if cursor.fetchone()[0] == 0:
                    self._insert_sample_inventory(cursor)
                
                conn.commit()
                logger.info("샘플 데이터 로드 완료")
                
        except Exception as e:
            logger.error(f"샘플 데이터 로드 실패: {e}")
    
    def _insert_sample_brands(self, cursor):
        """샘플 브랜드 데이터 삽입"""
        brands = [
            (1, "스타벅스", "카페"),
            (2, "맥도날드", "패스트푸드"),
            (3, "올리브영", "화장품")
        ]
        cursor.executemany(
            "INSERT INTO brands (id, name, industry) VALUES (?, ?, ?)",
            brands
        )
    
    def _insert_sample_branches(self, cursor):
        """샘플 매장 데이터 삽입"""
        branches = [
            (1, "강남점", 1, "서울시 강남구 테헤란로 123", "02-1234-5678", 1),
            (2, "홍대점", 1, "서울시 마포구 홍대로 456", "02-2345-6789", 2),
            (3, "부산점", 2, "부산시 해운대구 해운대로 789", "051-3456-7890", 3)
        ]
        cursor.executemany(
            "INSERT INTO branches (id, name, brand_id, address, phone, manager_id) VALUES (?, ?, ?, ?, ?, ?)",
            branches
        )
    
    def _insert_sample_employees(self, cursor):
        """샘플 직원 데이터 삽입"""
        employees = [
            (1, "김매니저", "kim_manager", "kim@example.com", "010-1111-1111", "매니저", "매장관리", 1, 1, 15000, 3000000),
            (2, "이직원", "lee_staff", "lee@example.com", "010-2222-2222", "직원", "서빙", 1, 1, 12000, 2500000),
            (3, "박주방", "park_kitchen", "park@example.com", "010-3333-3333", "주방장", "주방", 1, 1, 14000, 2800000),
            (4, "최서빙", "choi_service", "choi@example.com", "010-4444-4444", "직원", "서빙", 2, 1, 12000, 2500000),
            (5, "정청소", "jung_clean", "jung@example.com", "010-5555-5555", "직원", "청소", 1, 1, 11000, 2200000)
        ]
        cursor.executemany(
            "INSERT INTO employees (id, name, username, email, phone, position, department, branch_id, brand_id, hourly_wage, monthly_salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            employees
        )
    
    def _insert_sample_attendance(self, cursor):
        """샘플 출퇴근 데이터 삽입"""
        today = datetime.now()
        attendance_data = []
        
        for i in range(30):  # 최근 30일
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 주말 제외
            if date.weekday() >= 5:
                continue
            
            for emp_id in range(1, 6):
                # 출근 시간 (8:30 ~ 9:30)
                clock_in_hour = 9
                clock_in_minute = 0
                if emp_id == 3:  # 주방장은 8시 출근
                    clock_in_hour = 8
                elif emp_id == 5:  # 청소직원은 7시 출근
                    clock_in_hour = 7
                
                # 20% 확률로 지각
                import random
                if random.random() < 0.2:
                    clock_in_minute = random.randint(5, 45)
                
                clock_in = datetime.combine(date, datetime.min.time().replace(hour=clock_in_hour, minute=clock_in_minute))
                
                # 퇴근 시간 (17:00 ~ 22:00)
                clock_out_hour = 18
                clock_out_minute = 0
                
                # 30% 확률로 초과근무
                if random.random() < 0.3:
                    clock_out_hour = random.randint(18, 21)
                    clock_out_minute = random.randint(0, 59)
                
                clock_out = datetime.combine(date, datetime.min.time().replace(hour=clock_out_hour, minute=clock_out_minute))
                
                work_hours = (clock_out - clock_in).total_seconds() / 3600
                is_late = clock_in.time() > datetime.min.time().replace(hour=9, minute=0)
                is_overtime = work_hours > 8
                
                attendance_data.append((
                    emp_id, 1, date_str, clock_in, clock_out, work_hours, is_late, is_overtime, 'completed'
                ))
        
        cursor.executemany(
            "INSERT INTO attendance (employee_id, branch_id, date, clock_in, clock_out, work_hours, is_late, is_overtime, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            attendance_data
        )
    
    def _insert_sample_sales(self, cursor):
        """샘플 매출 데이터 삽입"""
        today = datetime.now()
        sales_data = []
        
        for i in range(30):  # 최근 30일
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 주말 제외
            if date.weekday() >= 5:
                continue
            
            # 매장별 매출
            for branch_id in [1, 2]:
                daily_sales = 500000 + (i * 10000)  # 점진적 증가
                
                # 직원별 매출 분배
                for emp_id in range(1, 6):
                    if emp_id <= 3:  # 매니저, 직원, 주방장
                        amount = daily_sales * 0.3 / 3  # 30% 분배
                    else:
                        amount = daily_sales * 0.35 / 2  # 35% 분배
                    
                    sales_data.append((
                        branch_id, emp_id, date_str, amount, 1, '음료', '카드', 'completed'
                    ))
        
        cursor.executemany(
            "INSERT INTO sales (branch_id, employee_id, date, amount, items_count, category, payment_method, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            sales_data
        )
    
    def _insert_sample_payroll(self, cursor):
        """샘플 급여 데이터 삽입"""
        payroll_data = []
        
        for year in [2023, 2024]:
            for month in range(1, 13):
                for emp_id in range(1, 6):
                    base_salary = 2500000 + (emp_id * 100000)  # 직급별 차등
                    work_hours = 160 + (emp_id * 10)  # 개인별 차등
                    attendance_days = 22
                    
                    # 초과근무 수당
                    overtime_hours = max(0, work_hours - 160)
                    overtime_pay = overtime_hours * 15000  # 시간당 15,000원
                    
                    # 성과 보너스
                    bonus = base_salary * 0.1  # 기본급의 10%
                    
                    # 공제
                    deduction = base_salary * 0.1  # 기본급의 10%
                    
                    net_salary = base_salary + overtime_pay + bonus - deduction
                    
                    payroll_data.append((
                        emp_id, 1, year, month, base_salary, overtime_pay, bonus, deduction, net_salary, work_hours, attendance_days
                    ))
        
        cursor.executemany(
            "INSERT INTO payroll (employee_id, branch_id, year, month, base_salary, overtime_pay, bonus, deduction, net_salary, work_hours, attendance_days) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            payroll_data
        )
    
    def _insert_sample_inventory(self, cursor):
        """샘플 재고 데이터 삽입"""
        inventory_data = [
            (1, "커피원두", "원재료", 50, 20, 100, 5000, "커피공급업체"),
            (1, "우유", "원재료", 30, 10, 80, 3000, "유제품업체"),
            (1, "시럽", "원재료", 25, 5, 50, 2000, "조미료업체"),
            (1, "종이컵", "소모품", 200, 50, 500, 100, "용품업체"),
            (1, "티슈", "소모품", 100, 20, 300, 500, "용품업체")
        ]
        
        cursor.executemany(
            "INSERT INTO inventory (branch_id, name, category, current_stock, min_stock, max_stock, unit_price, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            inventory_data
        )
    
    # === 데이터 조회 메서드들 ===

    def get_employees(
        self, 
        branch_id: int | None = None,  # pyright: ignore[reportGeneralTypeIssues]
        brand_id: int | None = None    # pyright: ignore[reportGeneralTypeIssues]
    ) -> List[Dict[str, Any]]:
        """직원 목록 조회"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    query = "SELECT * FROM employees WHERE status = 'active'"
                    params = []
                    
                    if branch_id:
                        query += " AND branch_id = ?"
                        params.append(branch_id)
                    
                    if brand_id:
                        query += " AND brand_id = ?"
                        params.append(brand_id)
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
            except Exception as e:
                logger.error(f"직원 목록 조회 실패: {e}")
                return []  # noqa

    def get_attendance_data(
        self,
        employee_id: int | None = None,  # pyright: ignore[reportGeneralTypeIssues]
        branch_id: int | None = None,    # pyright: ignore[reportGeneralTypeIssues]
        date_from: str | None = None,    # pyright: ignore[reportGeneralTypeIssues]
        date_to: str | None = None       # pyright: ignore[reportGeneralTypeIssues]
    ) -> List[Dict[str, Any]]:
        """출퇴근 데이터 조회"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    query = """
                        SELECT a.*, e.name as employee_name, e.position, b.name as branch_name
                        FROM attendance a
                        JOIN employees e ON a.employee_id = e.id
                        JOIN branches b ON a.branch_id = b.id
                        WHERE 1=1
                    """
                    params = []
                    
                    if employee_id:
                        query += " AND a.employee_id = ?"
                        params.append(employee_id)
                    
                    if branch_id:
                        query += " AND a.branch_id = ?"
                        params.append(branch_id)
                    
                    if date_from:
                        query += " AND a.date >= ?"
                        params.append(date_from)
                    
                    if date_to:
                        query += " AND a.date <= ?"
                        params.append(date_to)
                    
                    query += " ORDER BY a.date DESC, a.clock_in DESC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
            except Exception as e:
                logger.error(f"출퇴근 데이터 조회 실패: {e}")
                return []
    
    def get_sales_data(self, branch_id: int = None, employee_id: int = None,
                      date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """매출 데이터 조회"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    query = """
                        SELECT s.*, e.name as employee_name, b.name as branch_name
                        FROM sales s
                        JOIN employees e ON s.employee_id = e.id
                        JOIN branches b ON s.branch_id = b.id
                        WHERE s.status = 'completed'
                    """
                    params = []
                    
                    if branch_id:
                        query += " AND s.branch_id = ?"
                        params.append(branch_id)
                    
                    if employee_id:
                        query += " AND s.employee_id = ?"
                        params.append(employee_id)
                    
                    if date_from:
                        query += " AND s.date >= ?"
                        params.append(date_from)
                    
                    if date_to:
                        query += " AND s.date <= ?"
                        params.append(date_to)
                    
                    query += " ORDER BY s.date DESC, s.created_at DESC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
            except Exception as e:
                logger.error(f"매출 데이터 조회 실패: {e}")
                return []
    
    def get_payroll_data(self, employee_id: int = None, branch_id: int = None,
                        year: int = None, month: int = None) -> List[Dict[str, Any]]:
        """급여 데이터 조회"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    query = """
                        SELECT p.*, e.name as employee_name, b.name as branch_name
                        FROM payroll p
                        JOIN employees e ON p.employee_id = e.id
                        JOIN branches b ON p.branch_id = b.id
                        WHERE 1=1
                    """
                    params = []
                    
                    if employee_id:
                        query += " AND p.employee_id = ?"
                        params.append(employee_id)
                    
                    if branch_id:
                        query += " AND p.branch_id = ?"
                        params.append(branch_id)
                    
                    if year:
                        query += " AND p.year = ?"
                        params.append(year)
                    
                    if month:
                        query += " AND p.month = ?"
                        params.append(month)
                    
                    query += " ORDER BY p.year DESC, p.month DESC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
            except Exception as e:
                logger.error(f"급여 데이터 조회 실패: {e}")
                return []
    
    def get_integrated_analytics(self, branch_id: int, period: str = "month") -> Dict[str, Any]:
        """통합 분석 데이터 조회"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 기간 설정
                    if period == "week":
                        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    elif period == "month":
                        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    else:  # year
                        date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    
                    date_to = datetime.now().strftime('%Y-%m-%d')
                    
                    # 1. 출퇴근 통계
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_records,
                            SUM(CASE WHEN is_late = 1 THEN 1 ELSE 0 END) as late_count,
                            SUM(CASE WHEN is_overtime = 1 THEN 1 ELSE 0 END) as overtime_count,
                            AVG(work_hours) as avg_work_hours,
                            COUNT(DISTINCT employee_id) as active_employees
                        FROM attendance 
                        WHERE branch_id = ? AND date BETWEEN ? AND ?
                    """, (branch_id, date_from, date_to))
                    
                    attendance_stats = dict(cursor.fetchone())
                    
                    # 2. 매출 통계
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_sales,
                            SUM(amount) as total_amount,
                            AVG(amount) as avg_amount,
                            COUNT(DISTINCT employee_id) as sales_employees
                        FROM sales 
                        WHERE branch_id = ? AND date BETWEEN ? AND ? AND status = 'completed'
                    """, (branch_id, date_from, date_to))
                    
                    sales_stats = dict(cursor.fetchone())
                    
                    # 3. 급여 통계
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_payroll,
                            SUM(net_salary) as total_salary,
                            AVG(net_salary) as avg_salary,
                            SUM(work_hours) as total_work_hours
                        FROM payroll 
                        WHERE branch_id = ? AND year = ? AND month = ?
                    """, (branch_id, datetime.now().year, datetime.now().month))
                    
                    payroll_stats = dict(cursor.fetchone())
                    
                    # 4. 효율성 분석
                    total_sales = sales_stats.get('total_amount', 0)
                    total_salary = payroll_stats.get('total_salary', 0)
                    labor_cost_ratio = (total_salary / total_sales * 100) if total_sales > 0 else 0
                    
                    # 5. 개선 제안 생성
                    insights = []
                    recommendations = []
                    
                    if attendance_stats.get('late_count', 0) > attendance_stats.get('total_records', 0) * 0.1:
                        insights.append("지각률이 10%를 초과하고 있습니다.")
                        recommendations.append("출근 시간 관리 강화가 필요합니다.")
                    
                    if labor_cost_ratio > 30:
                        insights.append("인건비 비율이 30%를 초과하고 있습니다.")
                        recommendations.append("인력 효율성 개선이 필요합니다.")
                    
                    if sales_stats.get('avg_amount', 0) < 10000:
                        insights.append("평균 매출이 낮습니다.")
                        recommendations.append("업셀링 전략 수립이 필요합니다.")
                    
                    return {
                        "period": period,
                        "date_range": {"from": date_from, "to": date_to},
                        "attendance": attendance_stats,
                        "sales": sales_stats,
                        "payroll": payroll_stats,
                        "efficiency": {
                            "labor_cost_ratio": round(labor_cost_ratio, 2),
                            "sales_per_employee": round(total_sales / attendance_stats.get('active_employees', 1), 2),
                            "hours_per_sale": round(attendance_stats.get('avg_work_hours', 0) / max(sales_stats.get('total_sales', 1), 1), 2)
                        },
                        "insights": insights,
                        "recommendations": recommendations,
                        "generated_at": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"통합 분석 데이터 조회 실패: {e}")
                return {}
    
    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str = "info", priority: str = "normal") -> bool:
        """알림 생성"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO notifications (user_id, title, message, type, priority)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, title, message, notification_type, priority))
                    conn.commit()
                    return True
            except Exception as e:
                logger.error(f"알림 생성 실패: {e}")
                return False
    
    def get_notifications(self, user_id: int = None, is_read: bool = None) -> List[Dict[str, Any]]:
        """알림 목록 조회"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    query = "SELECT * FROM notifications WHERE 1=1"
                    params = []
                    
                    if user_id:
                        query += " AND user_id = ?"
                        params.append(user_id)
                    
                    if is_read is not None:
                        query += " AND is_read = ?"
                        params.append(is_read)
                    
                    query += " ORDER BY created_at DESC"
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
                    
            except Exception as e:
                logger.error(f"알림 목록 조회 실패: {e}")
                return []
    
    def save_analytics_result(self, branch_id: int, analysis_type: str, period: str, 
                            data: Dict[str, Any], insights: List[str], recommendations: List[str]) -> bool:
        """분석 결과 저장"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO analytics (branch_id, analysis_type, period, data, insights, recommendations)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (branch_id, analysis_type, period, json.dumps(data), 
                         json.dumps(insights), json.dumps(recommendations)))
                    conn.commit()
                    return True
            except Exception as e:
                logger.error(f"분석 결과 저장 실패: {e}")
                return False

# 전역 인스턴스
central_data = CentralDataLayer() 