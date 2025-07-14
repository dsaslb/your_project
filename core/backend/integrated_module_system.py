"""
통합 연동 모듈 시스템
모든 모듈이 중앙 데이터를 공유하고 실시간으로 연동되는 시스템
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.backend.central_data_layer import CentralDataLayer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleType(Enum):
    """모듈 타입"""
    ATTENDANCE = "attendance"
    SALES = "sales"
    PAYROLL = "payroll"
    INVENTORY = "inventory"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"

class IntegrationEvent(Enum):
    """통합 이벤트 타입"""
    ATTENDANCE_RECORDED = "attendance_recorded"
    SALES_RECORDED = "sales_recorded"
    PAYROLL_CALCULATED = "payroll_calculated"
    INVENTORY_UPDATED = "inventory_updated"
    ANALYTICS_GENERATED = "analytics_generated"
    ALERT_TRIGGERED = "alert_triggered"

@dataclass
class IntegrationEventData:
    """통합 이벤트 데이터"""
    event_type: IntegrationEvent
    module_id: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[int] = None
    branch_id: Optional[int] = None

class IntegratedModuleSystem:
    """통합 연동 모듈 시스템"""
    
    def __init__(self):
        self.central_data = CentralDataLayer()
        self.event_handlers: Dict[IntegrationEvent, List[Callable]] = {}
        self.module_registry: Dict[str, Dict[str, Any]] = {}
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        
        # 이벤트 핸들러 등록
        self._register_event_handlers()
        
        # 모듈 등록
        self._register_modules()
    
    def _register_event_handlers(self):
        """이벤트 핸들러 등록"""
        self.event_handlers[IntegrationEvent.ATTENDANCE_RECORDED] = [
            self._handle_attendance_recorded,
            self._trigger_analytics_update,
            self._check_efficiency_alerts
        ]
        
        self.event_handlers[IntegrationEvent.SALES_RECORDED] = [
            self._handle_sales_recorded,
            self._update_performance_metrics,
            self._trigger_analytics_update
        ]
        
        self.event_handlers[IntegrationEvent.PAYROLL_CALCULATED] = [
            self._handle_payroll_calculated,
            self._analyze_labor_cost,
            self._generate_efficiency_report
        ]
        
        self.event_handlers[IntegrationEvent.INVENTORY_UPDATED] = [
            self._handle_inventory_updated,
            self._check_stock_alerts,
            self._update_purchase_recommendations
        ]
        
        self.event_handlers[IntegrationEvent.ANALYTICS_GENERATED] = [
            self._handle_analytics_generated,
            self._create_management_notifications,
            self._update_dashboard_data
        ]
    
    def _register_modules(self):
        """모듈 등록"""
        self.module_registry = {
            "attendance_management": {
                "name": "출퇴근 관리",
                "type": ModuleType.ATTENDANCE,
                "version": "1.0.0",
                "dependencies": [],
                "integrations": ["sales", "payroll", "analytics"]
            },
            "sales_management": {
                "name": "매출 관리",
                "type": ModuleType.SALES,
                "version": "1.0.0",
                "dependencies": ["attendance"],
                "integrations": ["payroll", "analytics", "inventory"]
            },
            "payroll_management": {
                "name": "급여 관리",
                "type": ModuleType.PAYROLL,
                "version": "1.0.0",
                "dependencies": ["attendance", "sales"],
                "integrations": ["analytics"]
            },
            "inventory_management": {
                "name": "재고 관리",
                "type": ModuleType.INVENTORY,
                "version": "1.0.0",
                "dependencies": [],
                "integrations": ["sales", "analytics"]
            },
            "analytics_module": {
                "name": "통합 분석",
                "type": ModuleType.ANALYTICS,
                "version": "1.0.0",
                "dependencies": ["attendance", "sales", "payroll"],
                "integrations": ["notification"]
            }
        }
    
    def start_integration_system(self):
        """통합 시스템 시작"""
        self.running = True
        logger.info("통합 연동 모듈 시스템 시작")
        
        # 백그라운드 작업 시작
        threading.Thread(target=self._background_analytics_worker, daemon=True).start()
        threading.Thread(target=self._background_notification_worker, daemon=True).start()
    
    def stop_integration_system(self):
        """통합 시스템 중지"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("통합 연동 모듈 시스템 중지")
    
    def emit_event(self, event_data: IntegrationEventData):
        """이벤트 발생"""
        try:
            event_type = event_data.event_type
            if event_type in self.event_handlers:
                handlers = self.event_handlers[event_type]
                
                # 비동기로 이벤트 핸들러 실행
                for handler in handlers:
                    self.executor.submit(handler, event_data)
                
                logger.info(f"이벤트 발생: {event_type.value} - {event_data.module_id}")
            else:
                logger.warning(f"등록되지 않은 이벤트 타입: {event_type}")
                
        except Exception as e:
            logger.error(f"이벤트 처리 실패: {e}")
    
    # === 이벤트 핸들러들 ===
    
    def _handle_attendance_recorded(self, event_data: IntegrationEventData):
        """출퇴근 기록 이벤트 처리"""
        try:
            attendance_data = event_data.data
            employee_id = attendance_data.get('employee_id')
            branch_id = attendance_data.get('branch_id')
            
            # 1. 매출 데이터와 연동하여 효율성 분석
            sales_data = self.central_data.get_sales_data(
                employee_id=employee_id,
                branch_id=branch_id,
                date_from=attendance_data.get('date'),
                date_to=attendance_data.get('date')
            )
            
            if sales_data:
                # 근무 시간 대비 매출 효율성 계산
                work_hours = attendance_data.get('work_hours', 0)
                total_sales = sum(sale['amount'] for sale in sales_data)
                efficiency = total_sales / work_hours if work_hours > 0 else 0
                
                # 효율성 데이터 저장
                self.analysis_cache[f"efficiency_{employee_id}_{attendance_data.get('date')}"] = {
                    "employee_id": employee_id,
                    "branch_id": branch_id,
                    "date": attendance_data.get('date'),
                    "work_hours": work_hours,
                    "total_sales": total_sales,
                    "efficiency": efficiency,
                    "calculated_at": datetime.now().isoformat()
                }
            
            # 2. 급여 계산에 필요한 데이터 업데이트
            self._update_payroll_data(employee_id, branch_id, attendance_data)
            
            logger.info(f"출퇴근 기록 연동 처리 완료: 직원 {employee_id}")
            
        except Exception as e:
            logger.error(f"출퇴근 기록 이벤트 처리 실패: {e}")
    
    def _handle_sales_recorded(self, event_data: IntegrationEventData):
        """매출 기록 이벤트 처리"""
        try:
            sales_data = event_data.data
            employee_id = sales_data.get('employee_id')
            branch_id = sales_data.get('branch_id')
            
            # 1. 직원별 성과 업데이트
            self._update_employee_performance(employee_id, branch_id, sales_data)
            
            # 2. 매장별 매출 통계 업데이트
            self._update_branch_sales_stats(branch_id, sales_data)
            
            # 3. 재고 소모량 계산 및 업데이트
            self._update_inventory_consumption(branch_id, sales_data)
            
            logger.info(f"매출 기록 연동 처리 완료: 직원 {employee_id}")
            
        except Exception as e:
            logger.error(f"매출 기록 이벤트 처리 실패: {e}")
    
    def _handle_payroll_calculated(self, event_data: IntegrationEventData):
        """급여 계산 이벤트 처리"""
        try:
            payroll_data = event_data.data
            employee_id = payroll_data.get('employee_id')
            branch_id = payroll_data.get('branch_id')
            
            # 1. 인건비 효율성 분석
            self._analyze_labor_cost_efficiency(branch_id, payroll_data)
            
            # 2. 직원별 성과 대비 급여 분석
            self._analyze_salary_performance_ratio(employee_id, payroll_data)
            
            # 3. 매출 대비 인건비 비율 계산
            self._calculate_labor_cost_ratio(branch_id, payroll_data)
            
            logger.info(f"급여 계산 연동 처리 완료: 직원 {employee_id}")
            
        except Exception as e:
            logger.error(f"급여 계산 이벤트 처리 실패: {e}")
    
    def _handle_inventory_updated(self, event_data: IntegrationEventData):
        """재고 업데이트 이벤트 처리"""
        try:
            inventory_data = event_data.data
            branch_id = inventory_data.get('branch_id')
            
            # 1. 재고 부족 알림 생성
            self._check_low_stock_alerts(branch_id, inventory_data)
            
            # 2. 발주 추천 계산
            self._calculate_purchase_recommendations(branch_id, inventory_data)
            
            # 3. 재고 비용 분석
            self._analyze_inventory_costs(branch_id, inventory_data)
            
            logger.info(f"재고 업데이트 연동 처리 완료: 매장 {branch_id}")
            
        except Exception as e:
            logger.error(f"재고 업데이트 이벤트 처리 실패: {e}")
    
    def _handle_analytics_generated(self, event_data: IntegrationEventData):
        """분석 결과 생성 이벤트 처리"""
        try:
            analytics_data = event_data.data
            branch_id = analytics_data.get('branch_id')
            
            # 1. 관리자 알림 생성
            self._create_management_alerts(branch_id, analytics_data)
            
            # 2. 개선 제안 생성
            self._generate_improvement_suggestions(branch_id, analytics_data)
            
            # 3. 대시보드 데이터 업데이트
            self._update_dashboard_metrics(branch_id, analytics_data)
            
            logger.info(f"분석 결과 연동 처리 완료: 매장 {branch_id}")
            
        except Exception as e:
            logger.error(f"분석 결과 이벤트 처리 실패: {e}")
    
    # === 통합 분석 메서드들 ===
    
    def _trigger_analytics_update(self, event_data: IntegrationEventData):
        """분석 업데이트 트리거"""
        try:
            branch_id = event_data.data.get('branch_id')
            if branch_id:
                # 통합 분석 실행
                analytics_result = self.central_data.get_integrated_analytics(branch_id, "month")
                
                # 분석 결과 저장
                self.central_data.save_analytics_result(
                    branch_id=branch_id,
                    analysis_type="integrated",
                    period="month",
                    data=analytics_result,
                    insights=analytics_result.get('insights', []),
                    recommendations=analytics_result.get('recommendations', [])
                )
                
                # 분석 완료 이벤트 발생
                self.emit_event(IntegrationEventData(
                    event_type=IntegrationEvent.ANALYTICS_GENERATED,
                    module_id="analytics_module",
                    data={"branch_id": branch_id, "analytics": analytics_result},
                    timestamp=datetime.now(),
                    branch_id=branch_id
                ))
                
        except Exception as e:
            logger.error(f"분석 업데이트 트리거 실패: {e}")
    
    def _check_efficiency_alerts(self, event_data: IntegrationEventData):
        """효율성 알림 체크"""
        try:
            attendance_data = event_data.data
            employee_id = attendance_data.get('employee_id')
            branch_id = attendance_data.get('branch_id')
            
            # 지각 알림
            if attendance_data.get('is_late'):
                self.central_data.create_notification(
                    user_id=employee_id,
                    title="지각 알림",
                    message=f"{attendance_data.get('date')} 지각하셨습니다.",
                    notification_type="warning",
                    priority="normal"
                )
            
            # 초과근무 알림
            if attendance_data.get('is_overtime'):
                self.central_data.create_notification(
                    user_id=employee_id,
                    title="초과근무 알림",
                    message=f"{attendance_data.get('date')} 초과근무하셨습니다.",
                    notification_type="info",
                    priority="normal"
                )
            
            # 효율성 저하 알림 (매출 대비 근무시간)
            efficiency_key = f"efficiency_{employee_id}_{attendance_data.get('date')}"
            if efficiency_key in self.analysis_cache:
                efficiency_data = self.analysis_cache[efficiency_key]
                if efficiency_data.get('efficiency', 0) < 50000:  # 시간당 5만원 미만
                    self.central_data.create_notification(
                        user_id=employee_id,
                        title="효율성 개선 필요",
                        message="매출 대비 근무시간 효율성이 낮습니다.",
                        notification_type="warning",
                        priority="high"
                    )
            
        except Exception as e:
            logger.error(f"효율성 알림 체크 실패: {e}")
    
    def _analyze_labor_cost(self, event_data: IntegrationEventData):
        """인건비 분석"""
        try:
            payroll_data = event_data.data
            branch_id = payroll_data.get('branch_id')
            
            # 매출 데이터 조회
            sales_data = self.central_data.get_sales_data(
                branch_id=branch_id,
                date_from=f"{payroll_data.get('year')}-{payroll_data.get('month'):02d}-01",
                date_to=f"{payroll_data.get('year')}-{payroll_data.get('month'):02d}-31"
            )
            
            total_sales = sum(sale['amount'] for sale in sales_data)
            total_salary = payroll_data.get('net_salary', 0)
            
            if total_sales > 0:
                labor_cost_ratio = (total_salary / total_sales) * 100
                
                # 인건비 비율이 30%를 초과하면 관리자 알림
                if labor_cost_ratio > 30:
                    self.central_data.create_notification(
                        user_id=1,  # 관리자 ID
                        title="인건비 비율 경고",
                        message=f"매장 {branch_id}의 인건비 비율이 {labor_cost_ratio:.1f}%로 높습니다.",
                        notification_type="warning",
                        priority="high"
                    )
                
                # 분석 결과 저장
                self.analysis_cache[f"labor_cost_{branch_id}_{payroll_data.get('year')}_{payroll_data.get('month')}"] = {
                    "branch_id": branch_id,
                    "year": payroll_data.get('year'),
                    "month": payroll_data.get('month'),
                    "total_sales": total_sales,
                    "total_salary": total_salary,
                    "labor_cost_ratio": labor_cost_ratio,
                    "analyzed_at": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"인건비 분석 실패: {e}")
    
    def _generate_efficiency_report(self, event_data: IntegrationEventData):
        """효율성 리포트 생성"""
        try:
            payroll_data = event_data.data
            branch_id = payroll_data.get('branch_id')
            
            # 통합 분석 데이터 조회
            analytics_result = self.central_data.get_integrated_analytics(branch_id, "month")
            
            # 리포트 생성
            report = {
                "branch_id": branch_id,
                "period": "month",
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_employees": analytics_result.get('attendance', {}).get('active_employees', 0),
                    "total_sales": analytics_result.get('sales', {}).get('total_amount', 0),
                    "total_salary": analytics_result.get('payroll', {}).get('total_salary', 0),
                    "labor_cost_ratio": analytics_result.get('efficiency', {}).get('labor_cost_ratio', 0),
                    "avg_efficiency": analytics_result.get('efficiency', {}).get('sales_per_employee', 0)
                },
                "insights": analytics_result.get('insights', []),
                "recommendations": analytics_result.get('recommendations', [])
            }
            
            # 리포트 저장
            self.analysis_cache[f"efficiency_report_{branch_id}_{datetime.now().strftime('%Y%m')}"] = report
            
            # 관리자에게 리포트 알림
            self.central_data.create_notification(
                user_id=1,  # 관리자 ID
                title="효율성 리포트 생성 완료",
                message=f"매장 {branch_id}의 효율성 리포트가 생성되었습니다.",
                notification_type="info",
                priority="normal"
            )
            
        except Exception as e:
            logger.error(f"효율성 리포트 생성 실패: {e}")
    
    # === 백그라운드 작업자들 ===
    
    def _background_analytics_worker(self):
        """백그라운드 분석 작업자"""
        while self.running:
            try:
                # 매일 자정에 전체 분석 실행
                now = datetime.now()
                if now.hour == 0 and now.minute == 0:
                    self._run_daily_analytics()
                
                time.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                logger.error(f"백그라운드 분석 작업자 오류: {e}")
                time.sleep(60)
    
    def _background_notification_worker(self):
        """백그라운드 알림 작업자"""
        while self.running:
            try:
                # 미읽 알림 처리
                unread_notifications = self.central_data.get_notifications(is_read=False)
                
                for notification in unread_notifications:
                    # 알림 우선순위에 따른 처리
                    if notification['priority'] == 'high':
                        self._process_high_priority_notification(notification)
                
                time.sleep(30)  # 30초마다 체크
                
            except Exception as e:
                logger.error(f"백그라운드 알림 작업자 오류: {e}")
                time.sleep(30)
    
    def _run_daily_analytics(self):
        """일일 분석 실행"""
        try:
            # 모든 매장에 대해 분석 실행
            branches = [1, 2, 3]  # 샘플 매장 ID들
            
            for branch_id in branches:
                analytics_result = self.central_data.get_integrated_analytics(branch_id, "day")
                
                # 분석 결과 저장
                self.central_data.save_analytics_result(
                    branch_id=branch_id,
                    analysis_type="daily",
                    period="day",
                    data=analytics_result,
                    insights=analytics_result.get('insights', []),
                    recommendations=analytics_result.get('recommendations', [])
                )
                
                # 중요한 인사이트가 있으면 관리자 알림
                if analytics_result.get('insights'):
                    self.central_data.create_notification(
                        user_id=1,  # 관리자 ID
                        title="일일 분석 완료",
                        message=f"매장 {branch_id}의 일일 분석이 완료되었습니다.",
                        notification_type="info",
                        priority="normal"
                    )
            
            logger.info("일일 분석 완료")
            
        except Exception as e:
            logger.error(f"일일 분석 실행 실패: {e}")
    
    # === 공개 API 메서드들 ===
    
    def get_integrated_data(self, branch_id: int, data_types: List[str] = None) -> Dict[str, Any]:
        """통합 데이터 조회"""
        try:
            result = {}
            
            if not data_types or "attendance" in data_types:
                result["attendance"] = self.central_data.get_attendance_data(branch_id=branch_id)
            
            if not data_types or "sales" in data_types:
                result["sales"] = self.central_data.get_sales_data(branch_id=branch_id)
            
            if not data_types or "payroll" in data_types:
                result["payroll"] = self.central_data.get_payroll_data(branch_id=branch_id)
            
            if not data_types or "analytics" in data_types:
                result["analytics"] = self.central_data.get_integrated_analytics(branch_id)
            
            return result
            
        except Exception as e:
            logger.error(f"통합 데이터 조회 실패: {e}")
            return {}
    
    def get_efficiency_analysis(self, branch_id: int, period: str = "month") -> Dict[str, Any]:
        """효율성 분석 조회"""
        try:
            analytics_result = self.central_data.get_integrated_analytics(branch_id, period)
            
            # 추가 효율성 지표 계산
            efficiency_metrics = {
                "sales_per_hour": analytics_result.get('efficiency', {}).get('sales_per_employee', 0) / max(analytics_result.get('attendance', {}).get('avg_work_hours', 1), 1),
                "labor_cost_per_sale": analytics_result.get('efficiency', {}).get('labor_cost_ratio', 0) / 100,
                "attendance_rate": analytics_result.get('attendance', {}).get('total_records', 0) / max(analytics_result.get('attendance', {}).get('active_employees', 1), 1)
            }
            
            analytics_result['efficiency']['detailed_metrics'] = efficiency_metrics
            
            return analytics_result
            
        except Exception as e:
            logger.error(f"효율성 분석 조회 실패: {e}")
            return {}
    
    def get_management_dashboard(self, user_id: int) -> Dict[str, Any]:
        """관리자 대시보드 데이터"""
        try:
            # 사용자 권한에 따른 매장 목록 조회
            branches = [1, 2, 3]  # 실제로는 사용자 권한에 따라 조회
            
            dashboard_data = {
                "summary": {
                    "total_branches": len(branches),
                    "total_employees": 0,
                    "total_sales": 0,
                    "total_salary": 0
                },
                "branches": [],
                "alerts": [],
                "recent_analytics": []
            }
            
            for branch_id in branches:
                # 매장별 요약 데이터
                branch_data = self.get_integrated_data(branch_id)
                
                dashboard_data["summary"]["total_employees"] += len(branch_data.get("attendance", []))
                dashboard_data["summary"]["total_sales"] += sum(sale.get("amount", 0) for sale in branch_data.get("sales", []))
                dashboard_data["summary"]["total_salary"] += sum(pay.get("net_salary", 0) for pay in branch_data.get("payroll", []))
                
                # 매장별 상세 데이터
                dashboard_data["branches"].append({
                    "branch_id": branch_id,
                    "data": branch_data
                })
            
            # 알림 조회
            dashboard_data["alerts"] = self.central_data.get_notifications(user_id=user_id, is_read=False)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"관리자 대시보드 데이터 조회 실패: {e}")
            return {}

# 전역 인스턴스
integrated_system = IntegratedModuleSystem() 