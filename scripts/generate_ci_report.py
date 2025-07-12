#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD 리포트 생성 스크립트
CI/CD 파이프라인의 결과를 종합하여 HTML 리포트를 생성합니다.
"""

import os
import json
import yaml
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import jinja2

class CIReportGenerator:
    def __init__(self, artifacts_dir: str = "artifacts"):
        self.artifacts_dir = Path(artifacts_dir)
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "code_quality": {},
            "tests": {},
            "performance": {},
            "security": {},
            "plugins": {},
            "deployment": {}
        }
        
    def load_artifacts(self):
        """아티팩트 로드"""
        if not self.artifacts_dir.exists():
            print(f"아티팩트 디렉토리가 없습니다: {self.artifacts_dir}")
            return
        
        # 코드 품질 리포트 로드
        self.load_code_quality_reports()
        
        # 테스트 리포트 로드
        self.load_test_reports()
        
        # 성능 리포트 로드
        self.load_performance_reports()
        
        # 보안 리포트 로드
        self.load_security_reports()
        
        # 플러그인 리포트 로드
        self.load_plugin_reports()
        
        # 배포 리포트 로드
        self.load_deployment_reports()
        
        # 전체 요약 생성
        self.generate_summary()
    
    def load_code_quality_reports(self):
        """코드 품질 리포트 로드"""
        code_quality_dir = self.artifacts_dir / "code-quality-reports"
        if not code_quality_dir.exists():
            return
        
        # Bandit 보안 리포트
        bandit_file = code_quality_dir / "bandit-report.json"
        if bandit_file.exists():
            try:
                with open(bandit_file, 'r') as f:
                    self.report_data["code_quality"]["bandit"] = json.load(f)
            except Exception as e:
                print(f"Bandit 리포트 로드 실패: {e}")
        
        # Safety 취약점 리포트
        safety_file = code_quality_dir / "safety-report.json"
        if safety_file.exists():
            try:
                with open(safety_file, 'r') as f:
                    self.report_data["code_quality"]["safety"] = json.load(f)
            except Exception as e:
                print(f"Safety 리포트 로드 실패: {e}")
        
        # 커버리지 리포트
        coverage_files = list(code_quality_dir.glob("coverage.xml"))
        if coverage_files:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_files[0])
                root = tree.getroot()
                
                coverage_data = {}
                for package in root.findall(".//package"):
                    package_name = package.get("name", "unknown")
                    line_rate = float(package.get("line-rate", 0))
                    branch_rate = float(package.get("branch-rate", 0))
                    coverage_data[package_name] = {
                        "line_rate": line_rate * 100,
                        "branch_rate": branch_rate * 100
                    }
                
                self.report_data["code_quality"]["coverage"] = coverage_data
            except Exception as e:
                print(f"커버리지 리포트 로드 실패: {e}")
    
    def load_test_reports(self):
        """테스트 리포트 로드"""
        test_dirs = list(self.artifacts_dir.glob("test-coverage-*"))
        if not test_dirs:
            return
        
        test_data = {}
        for test_dir in test_dirs:
            python_version = test_dir.name.replace("test-coverage-", "")
            
            # 커버리지 데이터
            coverage_file = test_dir / "coverage.xml"
            if coverage_file.exists():
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(coverage_file)
                    root = tree.getroot()
                    
                    total_lines = 0
                    covered_lines = 0
                    
                    for line in root.findall(".//line"):
                        total_lines += 1
                        if line.get("hits", "0") != "0":
                            covered_lines += 1
                    
                    coverage_rate = (covered_lines / total_lines * 100) if total_lines > 0 else 0
                    
                    test_data[python_version] = {
                        "total_lines": total_lines,
                        "covered_lines": covered_lines,
                        "coverage_rate": coverage_rate
                    }
                except Exception as e:
                    print(f"테스트 커버리지 로드 실패 ({python_version}): {e}")
        
        self.report_data["tests"]["coverage"] = test_data
    
    def load_performance_reports(self):
        """성능 리포트 로드"""
        performance_dir = self.artifacts_dir / "performance-reports"
        if not performance_dir.exists():
            return
        
        # Locust 리포트
        locust_file = performance_dir / "locust-report.html"
        if locust_file.exists():
            self.report_data["performance"]["locust_report"] = str(locust_file)
        
        # 벤치마크 리포트
        benchmark_dir = performance_dir / ".benchmarks"
        if benchmark_dir.exists():
            benchmark_files = list(benchmark_dir.glob("*.json"))
            if benchmark_files:
                try:
                    with open(benchmark_files[0], 'r') as f:
                        benchmark_data = json.load(f)
                    
                    # 벤치마크 결과 정리
                    benchmarks = {}
                    for benchmark in benchmark_data.get("benchmarks", []):
                        name = benchmark.get("name", "unknown")
                        stats = benchmark.get("stats", {})
                        benchmarks[name] = {
                            "mean": stats.get("mean", 0),
                            "stddev": stats.get("stddev", 0),
                            "min": stats.get("min", 0),
                            "max": stats.get("max", 0)
                        }
                    
                    self.report_data["performance"]["benchmarks"] = benchmarks
                except Exception as e:
                    print(f"벤치마크 리포트 로드 실패: {e}")
    
    def load_security_reports(self):
        """보안 리포트 로드"""
        security_dir = self.artifacts_dir / "security-reports"
        if not security_dir.exists():
            return
        
        # Bandit 리포트
        bandit_file = security_dir / "bandit-report.json"
        if bandit_file.exists():
            try:
                with open(bandit_file, 'r') as f:
                    self.report_data["security"]["bandit"] = json.load(f)
            except Exception as e:
                print(f"보안 Bandit 리포트 로드 실패: {e}")
        
        # Safety 리포트
        safety_file = security_dir / "safety-report.json"
        if safety_file.exists():
            try:
                with open(safety_file, 'r') as f:
                    self.report_data["security"]["safety"] = json.load(f)
            except Exception as e:
                print(f"보안 Safety 리포트 로드 실패: {e}")
        
        # Semgrep 리포트
        semgrep_file = security_dir / "semgrep-report.json"
        if semgrep_file.exists():
            try:
                with open(semgrep_file, 'r') as f:
                    self.report_data["security"]["semgrep"] = json.load(f)
            except Exception as e:
                print(f"보안 Semgrep 리포트 로드 실패: {e}")
    
    def load_plugin_reports(self):
        """플러그인 리포트 로드"""
        # 플러그인 검증 리포트
        plugin_validation_files = glob.glob("plugin_validation_report_*.json")
        if plugin_validation_files:
            latest_file = max(plugin_validation_files, key=os.path.getctime)
            try:
                with open(latest_file, 'r') as f:
                    self.report_data["plugins"]["validation"] = json.load(f)
            except Exception as e:
                print(f"플러그인 검증 리포트 로드 실패: {e}")
        
        # 플러그인 테스트 리포트
        plugin_test_files = glob.glob("plugin_test_report_*.json")
        if plugin_test_files:
            latest_file = max(plugin_test_files, key=os.path.getctime)
            try:
                with open(latest_file, 'r') as f:
                    self.report_data["plugins"]["tests"] = json.load(f)
            except Exception as e:
                print(f"플러그인 테스트 리포트 로드 실패: {e}")
    
    def load_deployment_reports(self):
        """배포 리포트 로드"""
        # 배포 로그
        deployment_log_files = glob.glob("deployment_log_*.json")
        if deployment_log_files:
            latest_file = max(deployment_log_files, key=os.path.getctime)
            try:
                with open(latest_file, 'r') as f:
                    self.report_data["deployment"]["log"] = json.load(f)
            except Exception as e:
                print(f"배포 로그 로드 실패: {e}")
    
    def generate_summary(self):
        """전체 요약 생성"""
        summary = {
            "total_plugins": 0,
            "valid_plugins": 0,
            "test_coverage": 0,
            "security_issues": 0,
            "performance_score": 0,
            "deployment_status": "unknown"
        }
        
        # 플러그인 요약
        if "validation" in self.report_data["plugins"]:
            validation_data = self.report_data["plugins"]["validation"]
            summary["total_plugins"] = validation_data.get("summary", {}).get("total_plugins", 0)
            summary["valid_plugins"] = validation_data.get("summary", {}).get("valid_plugins", 0)
        
        # 테스트 커버리지 요약
        if "coverage" in self.report_data["tests"]:
            coverage_data = self.report_data["tests"]["coverage"]
            if coverage_data:
                # Python 3.11 기준으로 사용
                py311_data = coverage_data.get("3.11", {})
                summary["test_coverage"] = py311_data.get("coverage_rate", 0)
        
        # 보안 이슈 요약
        security_issues = 0
        if "bandit" in self.report_data["security"]:
            bandit_data = self.report_data["security"]["bandit"]
            security_issues += len(bandit_data.get("results", []))
        
        if "safety" in self.report_data["security"]:
            safety_data = self.report_data["security"]["safety"]
            security_issues += len(safety_data.get("vulnerabilities", []))
        
        summary["security_issues"] = security_issues
        
        # 성능 점수 계산
        if "benchmarks" in self.report_data["performance"]:
            benchmarks = self.report_data["performance"]["benchmarks"]
            if benchmarks:
                # 평균 응답 시간 기준으로 점수 계산
                avg_response_times = [b.get("mean", 0) for b in benchmarks.values()]
                if avg_response_times:
                    avg_time = sum(avg_response_times) / len(avg_response_times)
                    # 100ms 이하를 100점으로 하는 기준
                    summary["performance_score"] = max(0, 100 - (avg_time / 100 * 100))
        
        # 배포 상태
        if "log" in self.report_data["deployment"]:
            deployment_log = self.report_data["deployment"]["log"]
            if deployment_log:
                last_entry = deployment_log[-1]
                summary["deployment_status"] = last_entry.get("status", "unknown")
        
        self.report_data["summary"] = summary
    
    def generate_html_report(self) -> str:
        """HTML 리포트 생성"""
        template_str = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>플러그인 시스템 CI/CD 리포트</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
        }
        
        .summary-card h3 {
            color: #666;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .summary-card .value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .summary-card .status {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status.success { background-color: #d4edda; color: #155724; }
        .status.warning { background-color: #fff3cd; color: #856404; }
        .status.error { background-color: #f8d7da; color: #721c24; }
        .status.info { background-color: #d1ecf1; color: #0c5460; }
        
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        
        .metric-item h4 {
            color: #495057;
            margin-bottom: 5px;
        }
        
        .metric-item .value {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .table th,
        .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .table th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #495057;
        }
        
        .table tr:hover {
            background-color: #f5f5f5;
        }
        
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .badge.success { background-color: #d4edda; color: #155724; }
        .badge.warning { background-color: #fff3cd; color: #856404; }
        .badge.error { background-color: #f8d7da; color: #721c24; }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .chart-container {
            height: 300px;
            margin: 20px 0;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 30px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            .metric-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 플러그인 시스템 CI/CD 리포트</h1>
            <p>생성 시간: {{ report_data.timestamp }}</p>
        </div>
        
        <!-- 요약 섹션 -->
        <div class="summary-grid">
            <div class="summary-card">
                <h3>플러그인 상태</h3>
                <div class="value">{{ report_data.summary.valid_plugins }}/{{ report_data.summary.total_plugins }}</div>
                <div class="status {% if report_data.summary.valid_plugins == report_data.summary.total_plugins %}success{% else %}warning{% endif %}">
                    {% if report_data.summary.valid_plugins == report_data.summary.total_plugins %}모두 유효{% else %}일부 오류{% endif %}
                </div>
            </div>
            
            <div class="summary-card">
                <h3>테스트 커버리지</h3>
                <div class="value">{{ "%.1f"|format(report_data.summary.test_coverage) }}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ report_data.summary.test_coverage }}%"></div>
                </div>
                <div class="status {% if report_data.summary.test_coverage >= 80 %}success{% elif report_data.summary.test_coverage >= 60 %}warning{% else %}error{% endif %}">
                    {% if report_data.summary.test_coverage >= 80 %}우수{% elif report_data.summary.test_coverage >= 60 %}보통{% else %}부족{% endif %}
                </div>
            </div>
            
            <div class="summary-card">
                <h3>보안 이슈</h3>
                <div class="value">{{ report_data.summary.security_issues }}</div>
                <div class="status {% if report_data.summary.security_issues == 0 %}success{% elif report_data.summary.security_issues <= 5 %}warning{% else %}error{% endif %}">
                    {% if report_data.summary.security_issues == 0 %}안전{% elif report_data.summary.security_issues <= 5 %}주의{% else %}위험{% endif %}
                </div>
            </div>
            
            <div class="summary-card">
                <h3>성능 점수</h3>
                <div class="value">{{ "%.0f"|format(report_data.summary.performance_score) }}</div>
                <div class="status {% if report_data.summary.performance_score >= 80 %}success{% elif report_data.summary.performance_score >= 60 %}warning{% else %}error{% endif %}">
                    {% if report_data.summary.performance_score >= 80 %}우수{% elif report_data.summary.performance_score >= 60 %}보통{% else %}개선 필요{% endif %}
                </div>
            </div>
        </div>
        
        <!-- 플러그인 검증 결과 -->
        {% if report_data.plugins.validation %}
        <div class="section">
            <h2>🔍 플러그인 검증 결과</h2>
            <div class="metric-grid">
                <div class="metric-item">
                    <h4>총 플러그인</h4>
                    <div class="value">{{ report_data.plugins.validation.summary.total_plugins }}</div>
                </div>
                <div class="metric-item">
                    <h4>유효한 플러그인</h4>
                    <div class="value">{{ report_data.plugins.validation.summary.valid_plugins }}</div>
                </div>
                <div class="metric-item">
                    <h4>성공률</h4>
                    <div class="value">{{ "%.1f"|format(report_data.plugins.validation.summary.success_rate) }}%</div>
                </div>
            </div>
            
            {% if report_data.plugins.validation.plugins %}
            <table class="table">
                <thead>
                    <tr>
                        <th>플러그인</th>
                        <th>상태</th>
                        <th>오류</th>
                        <th>경고</th>
                    </tr>
                </thead>
                <tbody>
                    {% for plugin_name, plugin_data in report_data.plugins.validation.plugins.items() %}
                    <tr>
                        <td>{{ plugin_name }}</td>
                        <td>
                            <span class="badge {% if plugin_data.valid %}success{% else %}error{% endif %}">
                                {% if plugin_data.valid %}유효{% else %}오류{% endif %}
                            </span>
                        </td>
                        <td>{{ plugin_data.errors|length }}</td>
                        <td>{{ plugin_data.warnings|length }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- 테스트 커버리지 -->
        {% if report_data.tests.coverage %}
        <div class="section">
            <h2>🧪 테스트 커버리지</h2>
            <div class="metric-grid">
                {% for version, coverage in report_data.tests.coverage.items() %}
                <div class="metric-item">
                    <h4>Python {{ version }}</h4>
                    <div class="value">{{ "%.1f"|format(coverage.coverage_rate) }}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ coverage.coverage_rate }}%"></div>
                    </div>
                    <small>{{ coverage.covered_lines }}/{{ coverage.total_lines }} 라인</small>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <!-- 보안 검사 결과 -->
        {% if report_data.security %}
        <div class="section">
            <h2>🔒 보안 검사 결과</h2>
            
            {% if report_data.security.bandit %}
            <h3>Bandit 보안 검사</h3>
            <div class="metric-item">
                <h4>발견된 이슈</h4>
                <div class="value">{{ report_data.security.bandit.results|length }}</div>
            </div>
            {% endif %}
            
            {% if report_data.security.safety %}
            <h3>Safety 취약점 검사</h3>
            <div class="metric-item">
                <h4>취약한 패키지</h4>
                <div class="value">{{ report_data.security.safety.vulnerabilities|length }}</div>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- 성능 테스트 결과 -->
        {% if report_data.performance.benchmarks %}
        <div class="section">
            <h2>⚡ 성능 테스트 결과</h2>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
            
            <table class="table">
                <thead>
                    <tr>
                        <th>테스트</th>
                        <th>평균 (ms)</th>
                        <th>최소 (ms)</th>
                        <th>최대 (ms)</th>
                        <th>표준편차</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test_name, benchmark in report_data.performance.benchmarks.items() %}
                    <tr>
                        <td>{{ test_name }}</td>
                        <td>{{ "%.2f"|format(benchmark.mean * 1000) }}</td>
                        <td>{{ "%.2f"|format(benchmark.min * 1000) }}</td>
                        <td>{{ "%.2f"|format(benchmark.max * 1000) }}</td>
                        <td>{{ "%.2f"|format(benchmark.stddev * 1000) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <!-- 배포 상태 -->
        {% if report_data.deployment.log %}
        <div class="section">
            <h2>🚀 배포 상태</h2>
            <div class="metric-item">
                <h4>최종 상태</h4>
                <div class="value">
                    <span class="badge {% if report_data.summary.deployment_status == 'success' %}success{% else %}error{% endif %}">
                        {{ report_data.summary.deployment_status }}
                    </span>
                </div>
            </div>
            
            <h3>배포 로그</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>시간</th>
                        <th>단계</th>
                        <th>상태</th>
                        <th>메시지</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log_entry in report_data.deployment.log[-10:] %}
                    <tr>
                        <td>{{ log_entry.timestamp }}</td>
                        <td>{{ log_entry.step }}</td>
                        <td>
                            <span class="badge {% if log_entry.status == 'success' %}success{% elif log_entry.status == 'warning' %}warning{% else %}error{% endif %}">
                                {{ log_entry.status }}
                            </span>
                        </td>
                        <td>{{ log_entry.message }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>플러그인 시스템 CI/CD 리포트 | 생성 시간: {{ report_data.timestamp }}</p>
        </div>
    </div>
    
    {% if report_data.performance.benchmarks %}
    <script>
        // 성능 차트
        const ctx = document.getElementById('performanceChart').getContext('2d');
        const performanceData = {{ report_data.performance.benchmarks|tojson }};
        
        const labels = Object.keys(performanceData);
        const means = labels.map(label => performanceData[label].mean * 1000);
        const maxs = labels.map(label => performanceData[label].max * 1000);
        const mins = labels.map(label => performanceData[label].min * 1000);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '평균 응답 시간 (ms)',
                    data: means,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }, {
                    label: '최대 응답 시간 (ms)',
                    data: maxs,
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '응답 시간 (ms)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'API 성능 벤치마크'
                    }
                }
            }
        });
    </script>
    {% endif %}
</body>
</html>
        """
        
        template = jinja2.Template(template_str)
        return template.render(report_data=self.report_data)
    
    def save_report(self, output_file: str = "ci-report.html"):
        """리포트 저장"""
        html_content = self.generate_html_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"CI/CD 리포트가 생성되었습니다: {output_file}")
        return output_file

def main():
    """메인 함수"""
    generator = CIReportGenerator()
    
    print("CI/CD 리포트 생성 중...")
    generator.load_artifacts()
    
    output_file = generator.save_report()
    
    print(f"✅ 리포트 생성 완료: {output_file}")
    print(f"📊 요약:")
    
    summary = generator.report_data["summary"]
    print(f"  - 플러그인: {summary['valid_plugins']}/{summary['total_plugins']} 유효")
    print(f"  - 테스트 커버리지: {summary['test_coverage']:.1f}%")
    print(f"  - 보안 이슈: {summary['security_issues']}개")
    print(f"  - 성능 점수: {summary['performance_score']:.0f}점")
    print(f"  - 배포 상태: {summary['deployment_status']}")

if __name__ == "__main__":
    main() 