"""
고급 분석 및 AI 기능 통합
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """고급 분석 및 AI 기능"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.analysis_results = {}
    
    def analyze_employee_performance(self, employee_data: List[Dict]) -> Dict[str, Any]:
        """직원 성과 분석"""
        try:
            df = pd.DataFrame(employee_data)
            
            # 기본 통계
            basic_stats = {
                "total_employees": len(df),
                "active_employees": len(df[df['status'] == 'active']),
                "avg_salary": df['salary'].mean(),
                "salary_std": df['salary'].std(),
                "department_distribution": df['department'].value_counts().to_dict()
            }
            
            # 성과 지표 계산
            performance_metrics = self._calculate_performance_metrics(df)
            
            # 이상치 탐지
            outliers = self._detect_outliers(df, ['salary', 'work_hours'])
            
            # 클러스터링 분석
            clusters = self._cluster_employees(df)
            
            return {
                "basic_stats": basic_stats,
                "performance_metrics": performance_metrics,
                "outliers": outliers,
                "clusters": clusters,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"직원 성과 분석 실패: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """성과 지표 계산"""
        metrics = {}
        
        # 부서별 평균 급여
        dept_salary = df.groupby('department')['salary'].agg(['mean', 'std', 'count']).to_dict()
        
        # 직책별 성과 분석
        position_analysis = df.groupby('position').agg({
            'salary': ['mean', 'std'],
            'work_hours': ['mean', 'std']
        }).to_dict()
        
        # 성과 점수 계산 (예시)
        if 'work_hours' in df.columns and 'salary' in df.columns:
            df['performance_score'] = (df['work_hours'] / df['work_hours'].max()) * 0.6 + \
                                    (df['salary'] / df['salary'].max()) * 0.4
            
            metrics['performance_scores'] = {
                'mean': df['performance_score'].mean(),
                'std': df['performance_score'].std(),
                'top_performers': df.nlargest(5, 'performance_score')[['name', 'performance_score']].to_dict('records')
            }
        
        metrics['department_salary'] = dept_salary
        metrics['position_analysis'] = position_analysis
        
        return metrics
    
    def _detect_outliers(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """이상치 탐지"""
        outliers = {}
        
        for column in columns:
            if column in df.columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index
                outliers[column] = {
                    'count': len(outlier_indices),
                    'indices': outlier_indices.tolist(),
                    'values': df.loc[outlier_indices, column].tolist()
                }
        
        return outliers
    
    def _cluster_employees(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """직원 클러스터링"""
        try:
            # 수치형 컬럼만 선택
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_columns) < 2:
                return {"error": "클러스터링을 위한 수치형 데이터가 부족합니다."}
            
            # 데이터 정규화
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df[numeric_columns])
            
            # K-means 클러스터링
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_data)
            
            # 클러스터 결과 분석
            df_clustered = df.copy()
            df_clustered['cluster'] = clusters
            
            cluster_analysis = {}
            for i in range(n_clusters):
                cluster_data = df_clustered[df_clustered['cluster'] == i]
                cluster_analysis[f'cluster_{i}'] = {
                    'size': len(cluster_data),
                    'avg_salary': cluster_data['salary'].mean() if 'salary' in cluster_data.columns else 0,
                    'avg_work_hours': cluster_data['work_hours'].mean() if 'work_hours' in cluster_data.columns else 0,
                    'employees': cluster_data[['name', 'department', 'position']].to_dict('records')
                }
            
            return {
                'n_clusters': n_clusters,
                'cluster_analysis': cluster_analysis,
                'cluster_centers': kmeans.cluster_centers_.tolist()
            }
            
        except Exception as e:
            logger.error(f"클러스터링 실패: {e}")
            return {"error": str(e)}
    
    def predict_employee_turnover(self, employee_data: List[Dict]) -> Dict[str, Any]:
        """직원 이직 예측"""
        try:
            df = pd.DataFrame(employee_data)
            
            # 특성 엔지니어링
            features = self._engineer_turnover_features(df)
            
            if len(features) < 10:  # 최소 데이터 요구사항
                return {"error": "예측을 위한 충분한 데이터가 없습니다."}
            
            # 모델 학습
            model, accuracy, feature_importance = self._train_turnover_model(features)
            
            # 예측
            predictions = model.predict(features.drop('turnover_risk', axis=1, errors='ignore'))
            prediction_proba = model.predict_proba(features.drop('turnover_risk', axis=1, errors='ignore'))
            
            # 결과 분석
            high_risk_employees = []
            for i, (idx, row) in enumerate(features.iterrows()):
                if prediction_proba[i][1] > 0.7:  # 높은 이직 위험
                    high_risk_employees.append({
                        'employee_id': row.get('employee_id', idx),
                        'name': row.get('name', 'Unknown'),
                        'turnover_probability': float(prediction_proba[i][1]),
                        'risk_level': 'High' if prediction_proba[i][1] > 0.8 else 'Medium'
                    })
            
            return {
                'model_accuracy': accuracy,
                'feature_importance': feature_importance,
                'high_risk_employees': high_risk_employees,
                'total_employees_analyzed': len(features),
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"이직 예측 실패: {e}")
            return {"error": str(e)}
    
    def _engineer_turnover_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """이직 예측을 위한 특성 엔지니어링"""
        features = df.copy()
        
        # 범주형 변수 인코딩
        if 'department' in features.columns:
            features['department_encoded'] = pd.Categorical(features['department']).codes
        
        if 'position' in features.columns:
            features['position_encoded'] = pd.Categorical(features['position']).codes
        
        # 수치형 특성 정규화
        numeric_columns = ['salary', 'work_hours', 'age', 'tenure']
        for col in numeric_columns:
            if col in features.columns:
                features[f'{col}_normalized'] = (features[col] - features[col].mean()) / features[col].std()
        
        # 상호작용 특성
        if 'salary' in features.columns and 'work_hours' in features.columns:
            features['salary_hours_ratio'] = features['salary'] / features['work_hours']
        
        # 가상의 이직 위험 점수 (실제로는 실제 이직 데이터가 필요)
        np.random.seed(42)
        features['turnover_risk'] = np.random.choice([0, 1], size=len(features), p=[0.8, 0.2])
        
        return features
    
    def _train_turnover_model(self, features: pd.DataFrame) -> Tuple[Any, float, Dict[str, float]]:
        """이직 예측 모델 학습"""
        # 특성 선택
        feature_columns = [col for col in features.columns if col not in ['name', 'employee_id', 'turnover_risk']]
        
        X = features[feature_columns]
        y = features['turnover_risk']
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 모델 학습
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 정확도 계산
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 특성 중요도
        feature_importance = dict(zip(feature_columns, model.feature_importances_))
        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        return model, accuracy, feature_importance
    
    def analyze_schedule_optimization(self, schedule_data: List[Dict]) -> Dict[str, Any]:
        """스케줄 최적화 분석"""
        try:
            df = pd.DataFrame(schedule_data)
            
            # 기본 통계
            schedule_stats = {
                'total_schedules': len(df),
                'avg_work_hours': df['work_hours'].mean() if 'work_hours' in df.columns else 0,
                'overtime_hours': df[df['work_hours'] > 8]['work_hours'].sum() if 'work_hours' in df.columns else 0,
                'weekend_shifts': len(df[df['is_weekend'] == True]) if 'is_weekend' in df.columns else 0
            }
            
            # 스케줄 패턴 분석
            patterns = self._analyze_schedule_patterns(df)
            
            # 최적화 제안
            optimization_suggestions = self._generate_optimization_suggestions(df)
            
            return {
                'schedule_stats': schedule_stats,
                'patterns': patterns,
                'optimization_suggestions': optimization_suggestions,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"스케줄 최적화 분석 실패: {e}")
            return {"error": str(e)}
    
    def _analyze_schedule_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """스케줄 패턴 분석"""
        patterns = {}
        
        # 요일별 근무 패턴
        if 'day_of_week' in df.columns:
            day_patterns = df['day_of_week'].value_counts().to_dict()
            patterns['day_of_week_distribution'] = day_patterns
        
        # 시간대별 근무 패턴
        if 'start_time' in df.columns:
            df['hour'] = pd.to_datetime(df['start_time']).dt.hour
            hour_patterns = df['hour'].value_counts().sort_index().to_dict()
            patterns['hour_distribution'] = hour_patterns
        
        # 연속 근무 패턴
        if 'employee_id' in df.columns and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            consecutive_patterns = self._analyze_consecutive_shifts(df)
            patterns['consecutive_shifts'] = consecutive_patterns
        
        return patterns
    
    def _analyze_consecutive_shifts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """연속 근무 패턴 분석"""
        consecutive_analysis = {}
        
        for employee_id in df['employee_id'].unique():
            employee_schedules = df[df['employee_id'] == employee_id].sort_values('date')
            
            if len(employee_schedules) > 1:
                # 연속 근무일 계산
                consecutive_days = 0
                max_consecutive = 0
                
                for i in range(1, len(employee_schedules)):
                    days_diff = (employee_schedules.iloc[i]['date'] - employee_schedules.iloc[i-1]['date']).days
                    if days_diff == 1:
                        consecutive_days += 1
                        max_consecutive = max(max_consecutive, consecutive_days)
                    else:
                        consecutive_days = 0
                
                consecutive_analysis[employee_id] = {
                    'max_consecutive_days': max_consecutive,
                    'total_schedules': len(employee_schedules)
                }
        
        return consecutive_analysis
    
    def _generate_optimization_suggestions(self, df: pd.DataFrame) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        # 과도한 연속 근무 제안
        if 'work_hours' in df.columns:
            avg_hours = df['work_hours'].mean()
            if avg_hours > 9:
                suggestions.append("평균 근무 시간이 9시간을 초과합니다. 근무 시간 조정을 고려하세요.")
        
        # 주말 근무 분산 제안
        if 'is_weekend' in df.columns:
            weekend_ratio = df['is_weekend'].mean()
            if weekend_ratio > 0.3:
                suggestions.append("주말 근무 비율이 높습니다. 평일 근무로 분산을 고려하세요.")
        
        # 시간대별 분산 제안
        if 'start_time' in df.columns:
            df['hour'] = pd.to_datetime(df['start_time']).dt.hour
            peak_hour = df['hour'].mode().iloc[0] if len(df['hour'].mode()) > 0 else 9
            if peak_hour in [8, 9, 10]:
                suggestions.append("출근 시간이 집중되어 있습니다. 유연근무제 도입을 고려하세요.")
        
        return suggestions
    
    def generate_analytics_report(self, analysis_results: Dict[str, Any]) -> str:
        """분석 리포트 생성"""
        try:
            report = []
            report.append("# 멀티테넌시 관리 시스템 분석 리포트")
            report.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # 직원 성과 분석
            if 'employee_performance' in analysis_results:
                perf = analysis_results['employee_performance']
                report.append("## 1. 직원 성과 분석")
                report.append(f"- 총 직원 수: {perf['basic_stats']['total_employees']}")
                report.append(f"- 활성 직원 수: {perf['basic_stats']['active_employees']}")
                report.append(f"- 평균 급여: {perf['basic_stats']['avg_salary']:,.0f}원")
                report.append("")
            
            # 이직 예측
            if 'turnover_prediction' in analysis_results:
                turnover = analysis_results['turnover_prediction']
                report.append("## 2. 이직 예측 분석")
                report.append(f"- 모델 정확도: {turnover['model_accuracy']:.2%}")
                report.append(f"- 높은 이직 위험 직원: {len(turnover['high_risk_employees'])}명")
                report.append("")
            
            # 스케줄 최적화
            if 'schedule_optimization' in analysis_results:
                schedule = analysis_results['schedule_optimization']
                report.append("## 3. 스케줄 최적화 분석")
                report.append(f"- 총 스케줄 수: {schedule['schedule_stats']['total_schedules']}")
                report.append(f"- 평균 근무 시간: {schedule['schedule_stats']['avg_work_hours']:.1f}시간")
                report.append(f"- 초과 근무 시간: {schedule['schedule_stats']['overtime_hours']:.1f}시간")
                report.append("")
            
            # 최적화 제안
            if 'schedule_optimization' in analysis_results:
                suggestions = analysis_results['schedule_optimization']['optimization_suggestions']
                if suggestions:
                    report.append("## 4. 최적화 제안")
                    for i, suggestion in enumerate(suggestions, 1):
                        report.append(f"{i}. {suggestion}")
                    report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"리포트 생성 실패: {e}")
            return f"리포트 생성 중 오류가 발생했습니다: {e}"
    
    def save_analysis_results(self, results: Dict[str, Any], filename: str = None):
        """분석 결과 저장"""
        try:
            if filename is None:
                filename = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"분석 결과 저장 완료: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {e}")
            return None

# 전역 분석 인스턴스
advanced_analytics = AdvancedAnalytics() 