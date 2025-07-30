"""
리포트 자동화 스케줄러
엔터프라이즈급 자동 리포트 생성 및 배포 시스템
"""

import logging
import json
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from jinja2 import Template
import pdfkit
import weasyprint
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid
import hashlib
import os
import tempfile

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportType(Enum):
    """리포트 타입"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class DeliveryMethod(Enum):
    """배달 방법"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    FTP = "ftp"
    API = "api"

class ReportFormat(Enum):
    """리포트 형식"""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

@dataclass
class ReportSchedule:
    """리포트 스케줄"""
    id: str
    name: str
    description: str
    report_type: ReportType
    template_id: str
    parameters: Dict[str, Any]
    delivery_method: DeliveryMethod
    recipients: List[str]
    format: ReportFormat
    schedule_config: Dict[str, Any]
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class ReportExecution:
    """리포트 실행"""
    id: str
    schedule_id: str
    status: str  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    delivery_status: Dict[str, str] = None

class ReportScheduler:
    """리포트 스케줄러"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_connection = None
        self.redis_client = None
        self.schedules: Dict[str, ReportSchedule] = {}
        self.executions: Dict[str, ReportExecution] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        
        self._initialize_connections()
        self._load_schedules()
        self._setup_default_schedules()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            logger.info("리포트 스케줄러 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _load_schedules(self):
        """스케줄 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM report_schedules WHERE enabled = true
                    ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    schedule = ReportSchedule(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        report_type=ReportType(row['report_type']),
                        template_id=row['template_id'],
                        parameters=row['parameters'],
                        delivery_method=DeliveryMethod(row['delivery_method']),
                        recipients=row['recipients'],
                        format=ReportFormat(row['format']),
                        schedule_config=row['schedule_config'],
                        enabled=row['enabled'],
                        last_run=row['last_run'],
                        next_run=row['next_run'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                    self.schedules[schedule.id] = schedule
            
            logger.info(f"{len(self.schedules)}개의 스케줄 로드 완료")
            
        except Exception as e:
            logger.error(f"스케줄 로드 오류: {e}")
    
    def _setup_default_schedules(self):
        """기본 스케줄 설정"""
        try:
            # 일일 매출 리포트
            daily_sales_schedule = ReportSchedule(
                id=str(uuid.uuid4()),
                name="일일 매출 리포트",
                description="매일 오전 9시에 전일 매출 현황을 이메일로 전송",
                report_type=ReportType.DAILY,
                template_id="sales_dashboard",
                parameters={
                    'time_range': {'days': 1},
                    'include_charts': True,
                    'include_summary': True
                },
                delivery_method=DeliveryMethod.EMAIL,
                recipients=['sales@company.com', 'management@company.com'],
                format=ReportFormat.PDF,
                schedule_config={
                    'time': '09:00',
                    'timezone': 'Asia/Seoul',
                    'retry_on_failure': True,
                    'max_retries': 3
                },
                created_at=datetime.now()
            )
            
            # 주간 사용자 행동 리포트
            weekly_behavior_schedule = ReportSchedule(
                id=str(uuid.uuid4()),
                name="주간 사용자 행동 리포트",
                description="매주 월요일 오전 10시에 주간 사용자 행동 분석 리포트 전송",
                report_type=ReportType.WEEKLY,
                template_id="user_behavior_report",
                parameters={
                    'time_range': {'weeks': 1},
                    'include_segmentation': True,
                    'include_recommendations': True
                },
                delivery_method=DeliveryMethod.SLACK,
                recipients=['#analytics-team', '#product-team'],
                format=ReportFormat.HTML,
                schedule_config={
                    'day_of_week': 'monday',
                    'time': '10:00',
                    'timezone': 'Asia/Seoul'
                },
                created_at=datetime.now()
            )
            
            # 월간 비즈니스 성과 리포트
            monthly_performance_schedule = ReportSchedule(
                id=str(uuid.uuid4()),
                name="월간 비즈니스 성과 리포트",
                description="매월 1일 오전 11시에 월간 비즈니스 성과 종합 리포트 전송",
                report_type=ReportType.MONTHLY,
                template_id="business_performance",
                parameters={
                    'time_range': {'months': 1},
                    'include_forecasts': True,
                    'include_benchmarks': True
                },
                delivery_method=DeliveryMethod.EMAIL,
                recipients=['ceo@company.com', 'cfo@company.com', 'cto@company.com'],
                format=ReportFormat.PDF,
                schedule_config={
                    'day_of_month': 1,
                    'time': '11:00',
                    'timezone': 'Asia/Seoul'
                },
                created_at=datetime.now()
            )
            
            # 기본 스케줄 저장
            self.schedules[daily_sales_schedule.id] = daily_sales_schedule
            self.schedules[weekly_behavior_schedule.id] = weekly_behavior_schedule
            self.schedules[monthly_performance_schedule.id] = monthly_performance_schedule
            
            logger.info("기본 스케줄 설정 완료")
            
        except Exception as e:
            logger.error(f"기본 스케줄 설정 오류: {e}")
    
    async def start(self):
        """스케줄러 시작"""
        self.running = True
        logger.info("리포트 스케줄러 시작")
        
        # 스케줄 설정
        self._setup_schedules()
        
        # 스케줄러 루프 실행
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)  # 1분마다 체크
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        logger.info("리포트 스케줄러 중지")
    
    def _setup_schedules(self):
        """스케줄 설정"""
        try:
            for schedule_id, report_schedule in self.schedules.items():
                if not report_schedule.enabled:
                    continue
                
                # 스케줄 타입별 설정
                if report_schedule.report_type == ReportType.DAILY:
                    schedule.every().day.at(report_schedule.schedule_config['time']).do(
                        self._execute_schedule, schedule_id
                    )
                
                elif report_schedule.report_type == ReportType.WEEKLY:
                    day = report_schedule.schedule_config.get('day_of_week', 'monday')
                    time = report_schedule.schedule_config['time']
                    
                    if day == 'monday':
                        schedule.every().monday.at(time).do(self._execute_schedule, schedule_id)
                    elif day == 'tuesday':
                        schedule.every().tuesday.at(time).do(self._execute_schedule, schedule_id)
                    elif day == 'wednesday':
                        schedule.every().wednesday.at(time).do(self._execute_schedule, schedule_id)
                    elif day == 'thursday':
                        schedule.every().thursday.at(time).do(self._execute_schedule, schedule_id)
                    elif day == 'friday':
                        schedule.every().friday.at(time).do(self._execute_schedule, schedule_id)
                    elif day == 'saturday':
                        schedule.every().saturday.at(time).do(self._execute_schedule, schedule_id)
                    elif day == 'sunday':
                        schedule.every().sunday.at(time).do(self._execute_schedule, schedule_id)
                
                elif report_schedule.report_type == ReportType.MONTHLY:
                    day = report_schedule.schedule_config.get('day_of_month', 1)
                    time = report_schedule.schedule_config['time']
                    
                    # 매월 특정 날짜에 실행 (간단한 구현)
                    schedule.every().month.at(time).do(self._execute_schedule, schedule_id)
                
                elif report_schedule.report_type == ReportType.QUARTERLY:
                    # 분기별 실행
                    schedule.every(3).months.at(report_schedule.schedule_config['time']).do(
                        self._execute_schedule, schedule_id
                    )
                
                elif report_schedule.report_type == ReportType.YEARLY:
                    # 연간 실행
                    schedule.every().year.at(report_schedule.schedule_config['time']).do(
                        self._execute_schedule, schedule_id
                    )
            
            logger.info("모든 스케줄 설정 완료")
            
        except Exception as e:
            logger.error(f"스케줄 설정 오류: {e}")
    
    def _execute_schedule(self, schedule_id: str):
        """스케줄 실행"""
        try:
            report_schedule = self.schedules.get(schedule_id)
            if not report_schedule:
                logger.error(f"스케줄을 찾을 수 없습니다: {schedule_id}")
                return
            
            # 실행 ID 생성
            execution_id = str(uuid.uuid4())
            
            execution = ReportExecution(
                id=execution_id,
                schedule_id=schedule_id,
                status='pending',
                delivery_status={}
            )
            
            self.executions[execution_id] = execution
            
            # 비동기로 리포트 생성 및 배송
            self.executor.submit(self._generate_and_deliver_report, execution_id)
            
            logger.info(f"스케줄 실행 시작: {schedule_id} -> {execution_id}")
            
        except Exception as e:
            logger.error(f"스케줄 실행 오류: {e}")
    
    def _generate_and_deliver_report(self, execution_id: str):
        """리포트 생성 및 배송"""
        execution = self.executions[execution_id]
        report_schedule = self.schedules[execution.schedule_id]
        
        try:
            execution.status = 'running'
            execution.started_at = datetime.now()
            
            # 1. 리포트 생성
            report_file = self._generate_report(report_schedule)
            
            if report_file:
                execution.file_path = report_file
                execution.file_size = os.path.getsize(report_file)
                
                # 2. 리포트 배송
                delivery_results = self._deliver_report(report_schedule, report_file)
                execution.delivery_status = delivery_results
                
                execution.status = 'completed'
                execution.completed_at = datetime.now()
                
                # 스케줄 정보 업데이트
                report_schedule.last_run = datetime.now()
                report_schedule.next_run = self._calculate_next_run(report_schedule)
                
                logger.info(f"리포트 생성 및 배송 완료: {execution_id}")
                
            else:
                execution.status = 'failed'
                execution.error_message = '리포트 생성 실패'
                execution.completed_at = datetime.now()
                
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            
            logger.error(f"리포트 생성 및 배송 실패: {execution_id} - {e}")
    
    def _generate_report(self, report_schedule: ReportSchedule) -> Optional[str]:
        """리포트 생성"""
        try:
            # 1. 데이터 수집
            data = self._collect_report_data(report_schedule)
            
            # 2. 리포트 템플릿 적용
            report_content = self._apply_template(report_schedule, data)
            
            # 3. 형식별 파일 생성
            if report_schedule.format == ReportFormat.PDF:
                return self._generate_pdf(report_content, report_schedule)
            elif report_schedule.format == ReportFormat.HTML:
                return self._generate_html(report_content, report_schedule)
            elif report_schedule.format == ReportFormat.EXCEL:
                return self._generate_excel(data, report_schedule)
            elif report_schedule.format == ReportFormat.CSV:
                return self._generate_csv(data, report_schedule)
            elif report_schedule.format == ReportFormat.JSON:
                return self._generate_json(data, report_schedule)
            
            return None
            
        except Exception as e:
            logger.error(f"리포트 생성 오류: {e}")
            raise
    
    def _collect_report_data(self, report_schedule: ReportSchedule) -> Dict[str, Any]:
        """리포트 데이터 수집"""
        try:
            data = {
                'report_info': {
                    'name': report_schedule.name,
                    'type': report_schedule.report_type.value,
                    'generated_at': datetime.now().isoformat(),
                    'parameters': report_schedule.parameters
                },
                'analytics': {},
                'charts': {},
                'summary': {}
            }
            
            # BI 엔진에서 데이터 수집
            if hasattr(self, 'bi_engine'):
                # 템플릿별 분석 실행
                template = self.bi_engine.report_templates.get(report_schedule.template_id)
                if template:
                    for analysis in template.analyses:
                        analysis_id = self.bi_engine.create_analysis(
                            analysis_type=analysis['type'],
                            data_source=analysis['data_source'],
                            dimensions=analysis['dimensions'],
                            metrics=analysis['metrics'],
                            chart_type=analysis['chart_type']
                        )
                        
                        # 분석 결과 대기
                        for _ in range(30):  # 최대 30초 대기
                            result = self.bi_engine.get_analysis_result(analysis_id)
                            if result and 'error' not in result:
                                data['analytics'][analysis['id']] = result
                                break
                            time.sleep(1)
            
            # 데이터베이스에서 직접 데이터 수집
            data.update(self._collect_database_data(report_schedule))
            
            return data
            
        except Exception as e:
            logger.error(f"데이터 수집 오류: {e}")
            raise
    
    def _collect_database_data(self, report_schedule: ReportSchedule) -> Dict[str, Any]:
        """데이터베이스에서 데이터 수집"""
        try:
            data = {}
            
            # 시간 범위 계산
            time_range = report_schedule.parameters.get('time_range', {})
            end_date = datetime.now()
            
            if 'days' in time_range:
                start_date = end_date - timedelta(days=time_range['days'])
            elif 'weeks' in time_range:
                start_date = end_date - timedelta(weeks=time_range['weeks'])
            elif 'months' in time_range:
                start_date = end_date - timedelta(days=time_range['months'] * 30)
            else:
                start_date = end_date - timedelta(days=1)
            
            # 기본 통계 데이터 수집
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # 일일 매출 데이터
                cursor.execute("""
                    SELECT 
                        time_id,
                        total_sales,
                        total_orders,
                        unique_customers,
                        avg_order_value
                    FROM agg_daily_sales
                    WHERE time_id BETWEEN %s AND %s
                    ORDER BY time_id
                """, (start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')))
                
                data['daily_sales'] = [dict(row) for row in cursor.fetchall()]
                
                # 사용자 활동 데이터
                cursor.execute("""
                    SELECT 
                        time_id,
                        COUNT(*) as total_sessions,
                        AVG(session_duration) as avg_duration,
                        SUM(page_views) as total_page_views
                    FROM fact_user_activity
                    WHERE time_id BETWEEN %s AND %s
                    GROUP BY time_id
                    ORDER BY time_id
                """, (start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')))
                
                data['user_activity'] = [dict(row) for row in cursor.fetchall()]
                
                # 요약 통계
                cursor.execute("""
                    SELECT 
                        SUM(total_sales) as total_revenue,
                        SUM(total_orders) as total_orders,
                        COUNT(DISTINCT user_id) as unique_customers,
                        AVG(total_amount) as avg_order_value
                    FROM fact_sales
                    WHERE created_at BETWEEN %s AND %s
                """, (start_date, end_date))
                
                summary = cursor.fetchone()
                data['summary'] = dict(summary) if summary else {}
            
            return data
            
        except Exception as e:
            logger.error(f"데이터베이스 데이터 수집 오류: {e}")
            raise
    
    def _apply_template(self, report_schedule: ReportSchedule, data: Dict[str, Any]) -> str:
        """템플릿 적용"""
        try:
            # 기본 HTML 템플릿
            template_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{{ report_info.name }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
                    .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                    .chart { margin: 20px 0; text-align: center; }
                    .summary { background-color: #e9ecef; padding: 15px; border-radius: 5px; }
                    .metric { display: inline-block; margin: 10px; padding: 10px; background-color: white; border-radius: 3px; }
                    .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
                    .metric-label { font-size: 12px; color: #6c757d; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{{ report_info.name }}</h1>
                    <p>생성일: {{ report_info.generated_at }}</p>
                    <p>리포트 타입: {{ report_info.type }}</p>
                </div>
                
                <div class="summary">
                    <h2>요약 통계</h2>
                    {% if summary %}
                    <div class="metric">
                        <div class="metric-value">{{ "%.2f"|format(summary.total_revenue or 0) }}</div>
                        <div class="metric-label">총 매출</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ summary.total_orders or 0 }}</div>
                        <div class="metric-label">총 주문</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ summary.unique_customers or 0 }}</div>
                        <div class="metric-label">고유 고객</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ "%.2f"|format(summary.avg_order_value or 0) }}</div>
                        <div class="metric-label">평균 주문 금액</div>
                    </div>
                    {% endif %}
                </div>
                
                {% if daily_sales %}
                <div class="section">
                    <h2>일일 매출 트렌드</h2>
                    <div class="chart">
                        <img src="data:image/png;base64,{{ daily_sales_chart }}" alt="일일 매출 차트">
                    </div>
                </div>
                {% endif %}
                
                {% if user_activity %}
                <div class="section">
                    <h2>사용자 활동</h2>
                    <div class="chart">
                        <img src="data:image/png;base64,{{ user_activity_chart }}" alt="사용자 활동 차트">
                    </div>
                </div>
                {% endif %}
                
                <div class="section">
                    <h2>분석 결과</h2>
                    {% for analysis_id, analysis in analytics.items() %}
                    <div class="analysis">
                        <h3>{{ analysis_id }}</h3>
                        <p>{{ analysis.summary }}</p>
                    </div>
                    {% endfor %}
                </div>
            </body>
            </html>
            """
            
            # 차트 생성
            charts = {}
            if 'daily_sales' in data:
                charts['daily_sales_chart'] = self._create_daily_sales_chart(data['daily_sales'])
            if 'user_activity' in data:
                charts['user_activity_chart'] = self._create_user_activity_chart(data['user_activity'])
            
            # 템플릿 렌더링
            template = Template(template_html)
            html_content = template.render(
                report_info=data['report_info'],
                summary=data.get('summary', {}),
                daily_sales=data.get('daily_sales', []),
                user_activity=data.get('user_activity', []),
                analytics=data.get('analytics', {}),
                **charts
            )
            
            return html_content
            
        except Exception as e:
            logger.error(f"템플릿 적용 오류: {e}")
            raise
    
    def _create_daily_sales_chart(self, data: List[Dict[str, Any]]) -> str:
        """일일 매출 차트 생성"""
        try:
            if not data:
                return ""
            
            df = pd.DataFrame(data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['time_id'],
                y=df['total_sales'],
                mode='lines+markers',
                name='일일 매출',
                line=dict(color='#007bff', width=2)
            ))
            
            fig.update_layout(
                title='일일 매출 트렌드',
                xaxis_title='날짜',
                yaxis_title='매출 (원)',
                height=400,
                showlegend=True
            )
            
            # 차트를 base64로 인코딩
            img_bytes = fig.to_image(format="png")
            import base64
            return base64.b64encode(img_bytes).decode()
            
        except Exception as e:
            logger.error(f"일일 매출 차트 생성 오류: {e}")
            return ""
    
    def _create_user_activity_chart(self, data: List[Dict[str, Any]]) -> str:
        """사용자 활동 차트 생성"""
        try:
            if not data:
                return ""
            
            df = pd.DataFrame(data)
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('세션 수', '평균 세션 지속시간'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(
                go.Bar(x=df['time_id'], y=df['total_sessions'], name='세션 수'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df['time_id'], y=df['avg_duration'], name='평균 지속시간'),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True)
            
            # 차트를 base64로 인코딩
            img_bytes = fig.to_image(format="png")
            import base64
            return base64.b64encode(img_bytes).decode()
            
        except Exception as e:
            logger.error(f"사용자 활동 차트 생성 오류: {e}")
            return ""
    
    def _generate_pdf(self, html_content: str, report_schedule: ReportSchedule) -> str:
        """PDF 파일 생성"""
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            filename = f"report_{report_schedule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(temp_dir, filename)
            
            # HTML을 PDF로 변환
            weasyprint.HTML(string=html_content).write_pdf(filepath)
            
            return filepath
            
        except Exception as e:
            logger.error(f"PDF 생성 오류: {e}")
            raise
    
    def _generate_html(self, html_content: str, report_schedule: ReportSchedule) -> str:
        """HTML 파일 생성"""
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            filename = f"report_{report_schedule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(temp_dir, filename)
            
            # HTML 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return filepath
            
        except Exception as e:
            logger.error(f"HTML 생성 오류: {e}")
            raise
    
    def _generate_excel(self, data: Dict[str, Any], report_schedule: ReportSchedule) -> str:
        """Excel 파일 생성"""
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            filename = f"report_{report_schedule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(temp_dir, filename)
            
            # Excel 파일 생성
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 요약 시트
                if 'summary' in data:
                    summary_df = pd.DataFrame([data['summary']])
                    summary_df.to_excel(writer, sheet_name='요약', index=False)
                
                # 일일 매출 시트
                if 'daily_sales' in data:
                    sales_df = pd.DataFrame(data['daily_sales'])
                    sales_df.to_excel(writer, sheet_name='일일매출', index=False)
                
                # 사용자 활동 시트
                if 'user_activity' in data:
                    activity_df = pd.DataFrame(data['user_activity'])
                    activity_df.to_excel(writer, sheet_name='사용자활동', index=False)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Excel 생성 오류: {e}")
            raise
    
    def _generate_csv(self, data: Dict[str, Any], report_schedule: ReportSchedule) -> str:
        """CSV 파일 생성"""
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            filename = f"report_{report_schedule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(temp_dir, filename)
            
            # 주요 데이터를 CSV로 저장
            if 'daily_sales' in data:
                df = pd.DataFrame(data['daily_sales'])
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            return filepath
            
        except Exception as e:
            logger.error(f"CSV 생성 오류: {e}")
            raise
    
    def _generate_json(self, data: Dict[str, Any], report_schedule: ReportSchedule) -> str:
        """JSON 파일 생성"""
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            filename = f"report_{report_schedule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(temp_dir, filename)
            
            # JSON 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            return filepath
            
        except Exception as e:
            logger.error(f"JSON 생성 오류: {e}")
            raise
    
    def _deliver_report(self, report_schedule: ReportSchedule, file_path: str) -> Dict[str, str]:
        """리포트 배송"""
        try:
            delivery_results = {}
            
            if report_schedule.delivery_method == DeliveryMethod.EMAIL:
                delivery_results['email'] = self._send_email(report_schedule, file_path)
            
            elif report_schedule.delivery_method == DeliveryMethod.SLACK:
                delivery_results['slack'] = self._send_slack(report_schedule, file_path)
            
            elif report_schedule.delivery_method == DeliveryMethod.WEBHOOK:
                delivery_results['webhook'] = self._send_webhook(report_schedule, file_path)
            
            elif report_schedule.delivery_method == DeliveryMethod.FTP:
                delivery_results['ftp'] = self._send_ftp(report_schedule, file_path)
            
            elif report_schedule.delivery_method == DeliveryMethod.API:
                delivery_results['api'] = self._send_api(report_schedule, file_path)
            
            return delivery_results
            
        except Exception as e:
            logger.error(f"리포트 배송 오류: {e}")
            raise
    
    def _send_email(self, report_schedule: ReportSchedule, file_path: str) -> str:
        """이메일 전송"""
        try:
            # 이메일 설정
            smtp_config = self.config.get('smtp', {})
            
            # 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_email', 'noreply@company.com')
            msg['To'] = ', '.join(report_schedule.recipients)
            msg['Subject'] = f"[자동 리포트] {report_schedule.name}"
            
            # 본문 추가
            body = f"""
            안녕하세요,
            
            첨부된 파일은 {report_schedule.name}입니다.
            
            생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            리포트 타입: {report_schedule.report_type.value}
            
            감사합니다.
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 첨부파일 추가
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            msg.attach(part)
            
            # 이메일 전송
            with smtplib.SMTP(smtp_config.get('host', 'localhost'), smtp_config.get('port', 587)) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()
                
                if smtp_config.get('username'):
                    server.login(smtp_config['username'], smtp_config['password'])
                
                server.send_message(msg)
            
            return 'success'
            
        except Exception as e:
            logger.error(f"이메일 전송 오류: {e}")
            return f'failed: {str(e)}'
    
    def _send_slack(self, report_schedule: ReportSchedule, file_path: str) -> str:
        """Slack 전송"""
        try:
            slack_config = self.config.get('slack', {})
            webhook_url = slack_config.get('webhook_url')
            
            if not webhook_url:
                return 'failed: webhook_url not configured'
            
            # 파일 업로드
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'channels': report_schedule.recipients,
                    'title': report_schedule.name,
                    'initial_comment': f'자동 생성된 {report_schedule.name}입니다.'
                }
                
                response = requests.post(
                    'https://slack.com/api/files.upload',
                    headers={'Authorization': f"Bearer {slack_config.get('token')}"},
                    data=data,
                    files=files
                )
            
            if response.status_code == 200:
                return 'success'
            else:
                return f'failed: {response.status_code}'
            
        except Exception as e:
            logger.error(f"Slack 전송 오류: {e}")
            return f'failed: {str(e)}'
    
    def _send_webhook(self, report_schedule: ReportSchedule, file_path: str) -> str:
        """Webhook 전송"""
        try:
            webhook_config = self.config.get('webhook', {})
            webhook_url = webhook_config.get('url')
            
            if not webhook_url:
                return 'failed: webhook_url not configured'
            
            # 파일과 함께 POST 요청
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'report_name': report_schedule.name,
                    'report_type': report_schedule.report_type.value,
                    'generated_at': datetime.now().isoformat()
                }
                
                response = requests.post(webhook_url, data=data, files=files)
            
            if response.status_code in [200, 201]:
                return 'success'
            else:
                return f'failed: {response.status_code}'
            
        except Exception as e:
            logger.error(f"Webhook 전송 오류: {e}")
            return f'failed: {str(e)}'
    
    def _send_ftp(self, report_schedule: ReportSchedule, file_path: str) -> str:
        """FTP 전송"""
        try:
            ftp_config = self.config.get('ftp', {})
            
            # FTP 연결 및 파일 업로드
            import ftplib
            
            with ftplib.FTP() as ftp:
                ftp.connect(ftp_config.get('host', 'localhost'), ftp_config.get('port', 21))
                ftp.login(ftp_config.get('username'), ftp_config.get('password'))
                
                with open(file_path, 'rb') as f:
                    ftp.storbinary(f'STOR {os.path.basename(file_path)}', f)
            
            return 'success'
            
        except Exception as e:
            logger.error(f"FTP 전송 오류: {e}")
            return f'failed: {str(e)}'
    
    def _send_api(self, report_schedule: ReportSchedule, file_path: str) -> str:
        """API 전송"""
        try:
            api_config = self.config.get('api', {})
            api_url = api_config.get('url')
            
            if not api_url:
                return 'failed: api_url not configured'
            
            # API로 파일 전송
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'report_id': report_schedule.id,
                    'report_name': report_schedule.name,
                    'report_type': report_schedule.report_type.value
                }
                
                headers = {'Authorization': f"Bearer {api_config.get('token')}"}
                response = requests.post(api_url, data=data, files=files, headers=headers)
            
            if response.status_code in [200, 201]:
                return 'success'
            else:
                return f'failed: {response.status_code}'
            
        except Exception as e:
            logger.error(f"API 전송 오류: {e}")
            return f'failed: {str(e)}'
    
    def _calculate_next_run(self, report_schedule: ReportSchedule) -> datetime:
        """다음 실행 시간 계산"""
        try:
            now = datetime.now()
            
            if report_schedule.report_type == ReportType.DAILY:
                return now + timedelta(days=1)
            
            elif report_schedule.report_type == ReportType.WEEKLY:
                return now + timedelta(weeks=1)
            
            elif report_schedule.report_type == ReportType.MONTHLY:
                # 간단한 월 계산 (실제로는 더 정확한 로직 필요)
                return now + timedelta(days=30)
            
            elif report_schedule.report_type == ReportType.QUARTERLY:
                return now + timedelta(days=90)
            
            elif report_schedule.report_type == ReportType.YEARLY:
                return now + timedelta(days=365)
            
            return now + timedelta(days=1)
            
        except Exception as e:
            logger.error(f"다음 실행 시간 계산 오류: {e}")
            return datetime.now() + timedelta(days=1)
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> str:
        """스케줄 생성"""
        try:
            schedule_id = str(uuid.uuid4())
            
            schedule = ReportSchedule(
                id=schedule_id,
                name=schedule_data['name'],
                description=schedule_data.get('description', ''),
                report_type=ReportType(schedule_data['report_type']),
                template_id=schedule_data['template_id'],
                parameters=schedule_data.get('parameters', {}),
                delivery_method=DeliveryMethod(schedule_data['delivery_method']),
                recipients=schedule_data['recipients'],
                format=ReportFormat(schedule_data['format']),
                schedule_config=schedule_data['schedule_config'],
                enabled=schedule_data.get('enabled', True),
                created_at=datetime.now()
            )
            
            self.schedules[schedule_id] = schedule
            
            # 데이터베이스에 저장
            self._save_schedule_to_db(schedule)
            
            logger.info(f"스케줄 생성 완료: {schedule_id}")
            return schedule_id
            
        except Exception as e:
            logger.error(f"스케줄 생성 오류: {e}")
            raise
    
    def _save_schedule_to_db(self, schedule: ReportSchedule):
        """스케줄을 데이터베이스에 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO report_schedules 
                    (id, name, description, report_type, template_id, parameters, 
                     delivery_method, recipients, format, schedule_config, enabled, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    schedule.id,
                    schedule.name,
                    schedule.description,
                    schedule.report_type.value,
                    schedule.template_id,
                    json.dumps(schedule.parameters),
                    schedule.delivery_method.value,
                    schedule.recipients,
                    schedule.format.value,
                    json.dumps(schedule.schedule_config),
                    schedule.enabled,
                    schedule.created_at
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"스케줄 저장 오류: {e}")
            raise
    
    def get_schedule_status(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """스케줄 상태 조회"""
        try:
            schedule = self.schedules.get(schedule_id)
            if not schedule:
                return None
            
            return {
                'id': schedule.id,
                'name': schedule.name,
                'enabled': schedule.enabled,
                'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
                'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
                'delivery_method': schedule.delivery_method.value,
                'recipients': schedule.recipients
            }
            
        except Exception as e:
            logger.error(f"스케줄 상태 조회 오류: {e}")
            raise
    
    def get_execution_history(self, schedule_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """실행 이력 조회"""
        try:
            executions = [
                execution for execution in self.executions.values()
                if execution.schedule_id == schedule_id
            ]
            
            # 최신 순으로 정렬
            executions.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
            
            return [
                {
                    'id': execution.id,
                    'status': execution.status,
                    'started_at': execution.started_at.isoformat() if execution.started_at else None,
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'file_size': execution.file_size,
                    'error_message': execution.error_message,
                    'delivery_status': execution.delivery_status
                }
                for execution in executions[:limit]
            ]
            
        except Exception as e:
            logger.error(f"실행 이력 조회 오류: {e}")
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
            'db': 3
        },
        'smtp': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-password',
            'from_email': 'noreply@company.com',
            'use_tls': True
        },
        'slack': {
            'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
            'token': 'your-slack-token'
        }
    }
    
    # 스케줄러 생성 및 시작
    scheduler = ReportScheduler(config)
    
    # 스케줄러 실행
    asyncio.run(scheduler.start()) 