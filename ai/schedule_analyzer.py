#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스케줄 데이터 AI 분석 모듈
스케줄 데이터를 분석하여 인원 과다/부족, 효율성 개선안을 제시합니다.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

class ScheduleAnalyzer:
    """스케줄 데이터 AI 분석 및 개선 제안 생성기"""
    
    def __init__(self, templates_path: str = "analytics/report_templates.json"):
        """초기화"""
        self.templates = self._load_templates(templates_path)
        self.analysis_results = {}
        
    def _load_templates(self, templates_path: str) -> Dict:
        """템플릿 JSON 파일 로드"""
        try:
            with open(templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 기본 템플릿 제공
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict:
        """기본 템플릿 반환"""
        return {
            "schedule_analysis": {
                "excellent": "인력 배치가 최적화되어 있습니다.",
                "good": "전반적으로 양호한 인력 배치입니다.",
                "warning": "일부 시간대 인력 조정이 필요합니다.",
                "critical": "심각한 인력 배치 문제가 발견되었습니다."
            },
            "attendance_analysis": {
                "optimal": "출근률이 매우 양호합니다.",
                "acceptable": "출근률이 보통 수준입니다.",
                "concerning": "출근률 개선이 필요합니다.",
                "dangerous": "출근률이 심각한 수준입니다."
            },
            "work_hours_analysis": {
                "excellent": "근무 시간이 적절하게 배분되어 있습니다.",
                "good": "근무 시간 배분이 양호합니다.",
                "warning": "일부 직원의 근무 시간 조정이 필요합니다.",
                "critical": "근무 시간 배분에 심각한 문제가 있습니다."
            },
            "messages": {
                "overstaffed": "인원 과다 배치",
                "understaffed": "인원 부족",
                "overtime_warning": "과도한 초과근무",
                "attendance_issue": "출근률 문제",
                "efficiency_low": "업무 효율성 저하"
            },
            "icons": {
                "positive": "✅",
                "warning": "⚠️",
                "danger": "🚨",
                "info": "ℹ️"
            },
            "colors": {
                "success": "#10B981",
                "warning": "#F59E0B", 
                "danger": "#EF4444",
                "info": "#3B82F6"
            }
        }
    
    def analyze_schedule(self, schedule_data: List[Dict], 
                        attendance_data: List[Dict],
                        business_hours: Dict = None,
                        target_staffing: Dict = None) -> Dict[str, Any]:
        """
        스케줄 데이터 종합 분석
        
        Args:
            schedule_data: 스케줄 데이터 리스트
            attendance_data: 출근 데이터 리스트  
            business_hours: 영업시간 정보
            target_staffing: 목표 인력 배치 정보
            
        Returns:
            분석 결과 딕셔너리
        """
        # 데이터 전처리
        df_schedule = pd.DataFrame(schedule_data)
        df_attendance = pd.DataFrame(attendance_data)
        
        # 1. 인력 배치 분석
        staffing_analysis = self._analyze_staffing(df_schedule, target_staffing)
        
        # 2. 출근률 분석
        attendance_analysis = self._analyze_attendance(df_attendance)
        
        # 3. 근무 시간 분석
        work_hours_analysis = self._analyze_work_hours(df_schedule)
        
        # 4. 효율성 점수 계산
        efficiency_score = self._calculate_efficiency_score(
            staffing_analysis, attendance_analysis, work_hours_analysis
        )
        
        # 5. 문제점 식별
        issues = self._identify_issues(staffing_analysis, attendance_analysis, work_hours_analysis)
        
        # 6. 개선 제안 생성
        recommendations = self._generate_recommendations(issues, staffing_analysis)
        
        # 7. 결과 포맷팅
        result = {
            "analysis_date": datetime.now().isoformat(),
            "efficiency_score": efficiency_score,
            "staffing_analysis": staffing_analysis,
            "attendance_analysis": attendance_analysis,
            "work_hours_analysis": work_hours_analysis,
            "issues": issues,
            "recommendations": recommendations,
            "summary": self._generate_summary(efficiency_score, issues, recommendations)
        }
        
        self.analysis_results = result
        return result
    
    def _analyze_staffing(self, df_schedule: pd.DataFrame, 
                         target_staffing: Dict = None) -> Dict[str, Any]:
        """인력 배치 분석"""
        if df_schedule.empty:
            return {"status": "no_data", "score": 0, "details": "스케줄 데이터가 없습니다."}
        
        # 시간대별 인력 분석
        df_schedule['date'] = pd.to_datetime(df_schedule['date'])
        df_schedule['hour'] = pd.to_datetime(df_schedule['start_time']).dt.hour
        
        hourly_staffing = df_schedule.groupby(['date', 'hour']).size().reset_index(name='staff_count')
        
        # 과다/부족 인력 식별
        if target_staffing:
            target_count = target_staffing.get('target_per_hour', 3)
            overstaffed = hourly_staffing[hourly_staffing['staff_count'] > target_count * 1.2]
            understaffed = hourly_staffing[hourly_staffing['staff_count'] < target_count * 0.8]
        else:
            # 기본 기준: 평균 대비 ±20%
            mean_staff = hourly_staffing['staff_count'].mean()
            overstaffed = hourly_staffing[hourly_staffing['staff_count'] > mean_staff * 1.2]
            understaffed = hourly_staffing[hourly_staffing['staff_count'] < mean_staff * 0.8]
        
        # 점수 계산
        total_hours = len(hourly_staffing)
        overstaffed_hours = len(overstaffed)
        understaffed_hours = len(understaffed)
        
        if total_hours == 0:
            score = 0
        else:
            optimal_hours = total_hours - overstaffed_hours - understaffed_hours
            score = (optimal_hours / total_hours) * 100
        
        # JSON 직렬화를 위해 Timestamp를 문자열로 변환
        def convert_timestamps(data):
            if isinstance(data, dict):
                return {k: convert_timestamps(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_timestamps(item) for item in data]
            elif isinstance(data, pd.Timestamp):
                return data.isoformat()
            else:
                return data
        
        overstaffed_records = convert_timestamps(overstaffed.to_dict('records')) if not overstaffed.empty else []
        understaffed_records = convert_timestamps(understaffed.to_dict('records')) if not understaffed.empty else []
        
        return {
            "status": self._get_staffing_status(score),
            "score": round(score, 1),
            "total_hours_analyzed": total_hours,
            "overstaffed_hours": overstaffed_hours,
            "understaffed_hours": understaffed_hours,
            "overstaffed_details": overstaffed_records,
            "understaffed_details": understaffed_records
        }
    
    def _analyze_attendance(self, df_attendance: pd.DataFrame) -> Dict[str, Any]:
        """출근률 분석"""
        if df_attendance.empty:
            return {"status": "no_data", "score": 0, "details": "출근 데이터가 없습니다."}
        
        # 출근률 계산
        df_attendance['date'] = pd.to_datetime(df_attendance['date'])
        df_attendance['is_present'] = df_attendance['status'].isin(['present', 'on_time'])
        
        daily_attendance = df_attendance.groupby('date')['is_present'].agg(['count', 'sum']).reset_index()
        daily_attendance['attendance_rate'] = (daily_attendance['sum'] / daily_attendance['count']) * 100
        
        overall_rate = daily_attendance['attendance_rate'].mean()
        
        # 지각/결근 분석
        late_count = len(df_attendance[df_attendance['status'] == 'late'])
        absent_count = len(df_attendance[df_attendance['status'] == 'absent'])
        total_expected = len(df_attendance)
        
        # JSON 직렬화를 위해 Timestamp를 문자열로 변환
        def convert_timestamps(data):
            if isinstance(data, dict):
                return {k: convert_timestamps(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_timestamps(item) for item in data]
            elif isinstance(data, pd.Timestamp):
                return data.isoformat()
            else:
                return data
        
        daily_rates = convert_timestamps(daily_attendance.to_dict('records'))
        
        return {
            "status": self._get_attendance_status(overall_rate),
            "score": round(overall_rate, 1),
            "overall_attendance_rate": round(overall_rate, 1),
            "late_count": late_count,
            "absent_count": absent_count,
            "total_expected": total_expected,
            "daily_rates": daily_rates
        }
    
    def _analyze_work_hours(self, df_schedule: pd.DataFrame) -> Dict[str, Any]:
        """근무 시간 분석"""
        if df_schedule.empty:
            return {"status": "no_data", "score": 0, "details": "스케줄 데이터가 없습니다."}
        
        # 근무 시간 계산
        df_schedule['start_time'] = pd.to_datetime(df_schedule['start_time'])
        df_schedule['end_time'] = pd.to_datetime(df_schedule['end_time'])
        df_schedule['work_hours'] = (df_schedule['end_time'] - df_schedule['start_time']).dt.total_seconds() / 3600
        
        # 과도한 근무 시간 식별
        overtime_threshold = 8  # 8시간 초과를 과도한 근무로 간주
        excessive_hours = df_schedule[df_schedule['work_hours'] > overtime_threshold]
        
        # 평균 근무 시간
        avg_hours = df_schedule['work_hours'].mean()
        
        # 점수 계산 (8시간 기준으로 정규화)
        if avg_hours <= 8:
            score = 100 - (8 - avg_hours) * 10  # 8시간 미만 시 감점
        else:
            score = 100 - (avg_hours - 8) * 15  # 8시간 초과 시 더 큰 감점
        
        score = max(0, min(100, score))
        
        # JSON 직렬화를 위해 Timestamp를 문자열로 변환
        def convert_timestamps(data):
            if isinstance(data, dict):
                return {k: convert_timestamps(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_timestamps(item) for item in data]
            elif isinstance(data, pd.Timestamp):
                return data.isoformat()
            else:
                return data
        
        excessive_hours_records = convert_timestamps(excessive_hours.to_dict('records')) if not excessive_hours.empty else []
        
        return {
            "status": self._get_work_hours_status(score),
            "score": round(score, 1),
            "average_hours": round(avg_hours, 1),
            "excessive_hours_count": len(excessive_hours),
            "excessive_hours_details": excessive_hours_records,
            "overtime_threshold": overtime_threshold
        }
    
    def _calculate_efficiency_score(self, staffing: Dict, attendance: Dict, work_hours: Dict) -> float:
        """종합 효율성 점수 계산"""
        scores = []
        weights = [0.4, 0.35, 0.25]  # 인력배치, 출근률, 근무시간 가중치
        
        if staffing.get('score', 0) > 0:
            scores.append(staffing['score'])
        if attendance.get('score', 0) > 0:
            scores.append(attendance['score'])
        if work_hours.get('score', 0) > 0:
            scores.append(work_hours['score'])
        
        if not scores:
            return 0.0
        
        # 가중 평균 계산
        weighted_score = sum(score * weight for score, weight in zip(scores, weights[:len(scores)]))
        return round(weighted_score, 1)
    
    def _identify_issues(self, staffing: Dict, attendance: Dict, work_hours: Dict) -> List[str]:
        """문제점 식별"""
        issues = []
        
        # 인력 배치 문제
        if staffing.get('overstaffed_hours', 0) > 0:
            issues.append(f"인원 과다 배치: {staffing['overstaffed_hours']}시간")
        if staffing.get('understaffed_hours', 0) > 0:
            issues.append(f"인원 부족: {staffing['understaffed_hours']}시간")
        
        # 출근률 문제
        if attendance.get('overall_attendance_rate', 100) < 90:
            issues.append(f"출근률 저하: {attendance['overall_attendance_rate']}%")
        if attendance.get('late_count', 0) > 0:
            issues.append(f"지각 발생: {attendance['late_count']}건")
        
        # 근무 시간 문제
        if work_hours.get('excessive_hours_count', 0) > 0:
            issues.append(f"과도한 근무: {work_hours['excessive_hours_count']}건")
        
        return issues
    
    def _generate_recommendations(self, issues: List[str], staffing: Dict) -> List[str]:
        """개선 제안 생성"""
        recommendations = []
        
        for issue in issues:
            if "인원 과다" in issue:
                recommendations.append("과다 배치된 시간대의 인원을 다른 시간대로 재배치하거나 근무 시간을 조정하세요.")
            elif "인원 부족" in issue:
                recommendations.append("부족한 시간대에 아르바이트 직원을 추가 배정하거나 기존 직원의 근무 시간을 연장하세요.")
            elif "출근률" in issue:
                recommendations.append("출근률 개선을 위한 인센티브 제도 도입을 검토하세요.")
            elif "지각" in issue:
                recommendations.append("지각 방지를 위한 출근 시간 관리 시스템을 강화하세요.")
            elif "과도한 근무" in issue:
                recommendations.append("과도한 근무 시간을 줄이기 위해 인력 배치를 재조정하세요.")
        
        # 일반적인 개선 제안
        if not recommendations:
            recommendations.append("현재 스케줄이 양호합니다. 지속적인 모니터링을 유지하세요.")
        
        return recommendations
    
    def _generate_summary(self, efficiency_score: float, issues: List[str], 
                         recommendations: List[str]) -> str:
        """요약 메시지 생성"""
        if efficiency_score >= 90:
            summary = "전체적으로 매우 양호한 스케줄 관리 상태입니다."
        elif efficiency_score >= 70:
            summary = "전반적으로 양호하나 일부 개선이 필요합니다."
        elif efficiency_score >= 50:
            summary = "스케줄 관리에 개선이 필요합니다."
        else:
            summary = "스케줄 관리에 즉각적인 개선이 필요합니다."
        
        if issues:
            summary += f" 발견된 문제점: {len(issues)}개"
        
        return summary
    
    def _get_staffing_status(self, score: float) -> str:
        """인력 배치 상태 반환"""
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "warning"
        else:
            return "critical"
    
    def _get_attendance_status(self, rate: float) -> str:
        """출근률 상태 반환"""
        if rate >= 95:
            return "optimal"
        elif rate >= 85:
            return "acceptable"
        elif rate >= 70:
            return "concerning"
        else:
            return "dangerous"
    
    def _get_work_hours_status(self, score: float) -> str:
        """근무 시간 상태 반환"""
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "warning"
        else:
            return "critical"
    
    def format_report(self, analysis_result: Dict = None) -> Dict[str, Any]:
        """분석 결과를 리포트 형태로 포맷팅"""
        if analysis_result is None:
            analysis_result = self.analysis_results
        
        if not analysis_result:
            return {"error": "분석 결과가 없습니다."}
        
        # 템플릿에서 메시지 가져오기
        templates = self.templates
        
        formatted_report = {
            "date": analysis_result.get("analysis_date", datetime.now().isoformat()),
            "efficiency_score": analysis_result.get("efficiency_score", 0),
            "summary": analysis_result.get("summary", ""),
            "sections": {
                "staffing": {
                    "title": "인력 배치 분석",
                    "status": analysis_result.get("staffing_analysis", {}).get("status", "no_data"),
                    "score": analysis_result.get("staffing_analysis", {}).get("score", 0),
                    "message": templates.get("schedule_analysis", {}).get(
                        analysis_result.get("staffing_analysis", {}).get("status", "no_data"), 
                        "분석 데이터가 부족합니다."
                    ),
                    "details": analysis_result.get("staffing_analysis", {})
                },
                "attendance": {
                    "title": "출근률 분석",
                    "status": analysis_result.get("attendance_analysis", {}).get("status", "no_data"),
                    "score": analysis_result.get("attendance_analysis", {}).get("score", 0),
                    "message": templates.get("attendance_analysis", {}).get(
                        analysis_result.get("attendance_analysis", {}).get("status", "no_data"),
                        "분석 데이터가 부족합니다."
                    ),
                    "details": analysis_result.get("attendance_analysis", {})
                },
                "work_hours": {
                    "title": "근무 시간 분석",
                    "status": analysis_result.get("work_hours_analysis", {}).get("status", "no_data"),
                    "score": analysis_result.get("work_hours_analysis", {}).get("score", 0),
                    "message": templates.get("work_hours_analysis", {}).get(
                        analysis_result.get("work_hours_analysis", {}).get("status", "no_data"),
                        "분석 데이터가 부족합니다."
                    ),
                    "details": analysis_result.get("work_hours_analysis", {})
                }
            },
            "issues": analysis_result.get("issues", []),
            "recommendations": analysis_result.get("recommendations", []),
            "visual_indicators": {
                "icon": self._get_overall_icon(analysis_result.get("efficiency_score", 0)),
                "color": self._get_overall_color(analysis_result.get("efficiency_score", 0))
            }
        }
        
        return formatted_report
    
    def _get_overall_icon(self, score: float) -> str:
        """전체 점수에 따른 아이콘 반환"""
        if score >= 90:
            return self.templates.get("icons", {}).get("positive", "✅")
        elif score >= 70:
            return self.templates.get("icons", {}).get("warning", "⚠️")
        else:
            return self.templates.get("icons", {}).get("danger", "🚨")
    
    def _get_overall_color(self, score: float) -> str:
        """전체 점수에 따른 색상 반환"""
        if score >= 90:
            return self.templates.get("colors", {}).get("success", "#10B981")
        elif score >= 70:
            return self.templates.get("colors", {}).get("warning", "#F59E0B")
        else:
            return self.templates.get("colors", {}).get("danger", "#EF4444")


# 사용 예시
if __name__ == "__main__":
    # 샘플 데이터
    sample_schedule_data = [
        {
            "date": "2025-01-07",
            "employee_id": 1,
            "start_time": "2025-01-07 09:00:00",
            "end_time": "2025-01-07 17:00:00",
            "position": "매니저"
        },
        {
            "date": "2025-01-07", 
            "employee_id": 2,
            "start_time": "2025-01-07 10:00:00",
            "end_time": "2025-01-07 18:00:00",
            "position": "직원"
        }
    ]
    
    sample_attendance_data = [
        {
            "date": "2025-01-07",
            "employee_id": 1,
            "status": "present",
            "check_in": "2025-01-07 08:55:00"
        },
        {
            "date": "2025-01-07",
            "employee_id": 2, 
            "status": "late",
            "check_in": "2025-01-07 10:15:00"
        }
    ]
    
    # 분석기 초기화 및 실행
    analyzer = ScheduleAnalyzer()
    result = analyzer.analyze_schedule(sample_schedule_data, sample_attendance_data)
    formatted_report = analyzer.format_report(result)
    
    print("=== AI 스케줄 분석 결과 ===")
    print(json.dumps(formatted_report, indent=2, ensure_ascii=False))
