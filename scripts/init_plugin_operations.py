#!/usr/bin/env python3
"""
플러그인 운영 및 모니터링 시스템 초기화 스크립트
실제 운영 환경에서 플러그인 시스템의 안정성과 성능을 관리하는 시스템을 초기화
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/plugin_operations_init.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def init_plugin_operations():
    """플러그인 운영 및 모니터링 시스템 초기화"""
    logger.info("=== 플러그인 운영 및 모니터링 시스템 초기화 시작 ===")
    
    try:
        # 1. 플러그인 운영 관리자 초기화
        logger.info("1. 플러그인 운영 관리자 초기화")
        from core.backend.plugin_operations_manager import plugin_operations_manager
        
        # 2. 운영 모니터링 시작
        logger.info("2. 운영 모니터링 시작")
        start_result = plugin_operations_manager.start_operations()
        logger.info(f"운영 모니터링 시작 결과: {start_result}")
        
        # 3. 초기 상태 확인
        logger.info("3. 초기 상태 확인")
        status = plugin_operations_manager.get_operations_status()
        logger.info(f"초기 상태: {status}")
        
        # 4. 임계값 설정
        logger.info("4. 임계값 설정")
        thresholds = {
            'max_response_time': 5.0,
            'max_memory_usage': 80.0,
            'max_cpu_usage': 90.0,
            'max_error_rate': 10.0,
            'max_plugin_load_time': 10.0
        }
        
        for name, value in thresholds.items():
            success = plugin_operations_manager.set_threshold(name, value)
            if success:
                logger.info(f"  임계값 설정 완료: {name} = {value}")
            else:
                logger.warning(f"  임계값 설정 실패: {name}")
        
        # 5. 샘플 운영 로그 기록
        logger.info("5. 샘플 운영 로그 기록")
        sample_operations = [
            ('plugin_load', True, 2.5, {'plugin_name': 'sample_plugin'}),
            ('api_call', True, 0.8, {'endpoint': '/api/test'}),
            ('database_query', True, 1.2, {'table': 'users'}),
            ('file_operation', False, 5.5, {'file': 'config.json'}),
        ]
        
        for op_type, success, response_time, details in sample_operations:
            plugin_operations_manager.record_operation(
                operation_type=op_type,
                success=success,
                response_time=response_time,
                details=details
            )
            logger.info(f"  샘플 로그 기록: {op_type} - {'성공' if success else '실패'}")
        
        # 6. 성능 메트릭 확인
        logger.info("6. 성능 메트릭 확인")
        metrics = plugin_operations_manager.get_performance_metrics()
        logger.info(f"  성능 메트릭: {len(metrics.get('response_times', []))}개 응답 시간 기록")
        
        # 7. 알림 확인
        logger.info("7. 알림 확인")
        alerts = plugin_operations_manager.get_alerts()
        logger.info(f"  알림 수: {len(alerts)}개")
        
        # 8. 헬스 체크 실행
        logger.info("8. 헬스 체크 실행")
        health_status = plugin_operations_manager._perform_health_check()
        logger.info(f"  헬스 상태: {health_status['overall_status']}")
        
        logger.info("=== 플러그인 운영 및 모니터링 시스템 초기화 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"플러그인 운영 및 모니터링 시스템 초기화 실패: {e}")
        return False

def test_plugin_operations_apis():
    """플러그인 운영 및 모니터링 API 테스트"""
    logger.info("=== 플러그인 운영 및 모니터링 API 테스트 시작 ===")
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # API 엔드포인트 테스트
        test_endpoints = [
            ("/api/plugin-operations/status", "GET"),
            ("/api/plugin-operations/metrics", "GET"),
            ("/api/plugin-operations/alerts", "GET"),
            ("/api/plugin-operations/thresholds", "GET"),
            ("/api/plugin-operations/health", "GET"),
            ("/api/plugin-operations/logs", "GET"),
        ]
        
        for endpoint, method in test_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    logger.info(f"  [OK] {endpoint}: 성공")
                else:
                    logger.warning(f"  [WARN] {endpoint}: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"  [ERROR] {endpoint}: 실패 - {e}")
        
        # POST 엔드포인트 테스트
        post_endpoints = [
            ("/api/plugin-operations/start", {}),
            ("/api/plugin-operations/record", {
                "operation_type": "test_operation",
                "success": True,
                "response_time": 1.5,
                "details": {"test": True}
            }),
        ]
        
        for endpoint, data in post_endpoints:
            try:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
                if response.status_code == 200:
                    logger.info(f"  [OK] {endpoint}: 성공")
                else:
                    logger.warning(f"  [WARN] {endpoint}: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"  [ERROR] {endpoint}: 실패 - {e}")
        
        logger.info("=== 플러그인 운영 및 모니터링 API 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"API 테스트 실패: {e}")
        return False

def create_operations_dashboard():
    """운영 대시보드 생성"""
    logger.info("=== 운영 대시보드 생성 ===")
    
    try:
        # 대시보드 디렉토리 생성
        dashboard_dir = Path("static/operations_dashboard")
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # 대시보드 HTML 파일 생성
        dashboard_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>플러그인 운영 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .metric-label { color: #666; }
        .status { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; }
        .status.running { background: #28a745; }
        .status.stopped { background: #dc3545; }
        .chart-container { position: relative; height: 300px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>플러그인 운영 대시보드</h1>
            <p>실시간 플러그인 시스템 모니터링</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>운영 상태</h3>
                <div class="metric">
                    <div id="status" class="status">확인 중...</div>
                    <div class="metric-label">시스템 상태</div>
                </div>
                <div class="metric">
                    <div id="uptime" class="metric-value">00:00:00</div>
                    <div class="metric-label">가동 시간</div>
                </div>
            </div>
            
            <div class="card">
                <h3>성능 메트릭</h3>
                <div class="metric">
                    <div id="success-rate" class="metric-value">0%</div>
                    <div class="metric-label">성공률</div>
                </div>
                <div class="metric">
                    <div id="avg-response" class="metric-value">0.00초</div>
                    <div class="metric-label">평균 응답 시간</div>
                </div>
            </div>
            
            <div class="card">
                <h3>시스템 리소스</h3>
                <div class="metric">
                    <div id="memory-usage" class="metric-value">0%</div>
                    <div class="metric-label">메모리 사용량</div>
                </div>
                <div class="metric">
                    <div id="cpu-usage" class="metric-value">0%</div>
                    <div class="metric-label">CPU 사용량</div>
                </div>
            </div>
            
            <div class="card">
                <h3>알림</h3>
                <div class="metric">
                    <div id="alert-count" class="metric-value">0</div>
                    <div class="metric-label">활성 알림</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>응답 시간 추이</h3>
            <div class="chart-container">
                <canvas id="responseChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h3>최근 알림</h3>
            <div id="alerts-list"></div>
        </div>
    </div>
    
    <script>
        // 차트 초기화
        const ctx = document.getElementById('responseChart').getContext('2d');
        const responseChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '응답 시간 (초)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // 데이터 업데이트 함수
        async function updateDashboard() {
            try {
                const response = await fetch('/api/plugin-operations/status');
                const data = await response.json();
                
                if (data.status === 'success') {
                    const status = data.data;
                    
                    // 운영 상태 업데이트
                    const statusElement = document.getElementById('status');
                    if (status.operations_status.running) {
                        statusElement.textContent = '실행 중';
                        statusElement.className = 'status running';
                    } else {
                        statusElement.textContent = '중지됨';
                        statusElement.className = 'status stopped';
                    }
                    
                    // 가동 시간 업데이트
                    const uptime = status.operations_status.uptime;
                    const hours = Math.floor(uptime / 3600);
                    const minutes = Math.floor((uptime % 3600) / 60);
                    const seconds = uptime % 60;
                    document.getElementById('uptime').textContent = 
                        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    
                    // 성능 메트릭 업데이트
                    const perf = status.performance_summary;
                    document.getElementById('success-rate').textContent = perf.success_rate.toFixed(1) + '%';
                    document.getElementById('avg-response').textContent = perf.avg_response_time.toFixed(2) + '초';
                    document.getElementById('memory-usage').textContent = perf.current_memory_usage.toFixed(1) + '%';
                    document.getElementById('cpu-usage').textContent = perf.current_cpu_usage.toFixed(1) + '%';
                    
                    // 알림 수 업데이트
                    document.getElementById('alert-count').textContent = status.recent_alerts.length;
                    
                    // 알림 목록 업데이트
                    const alertsList = document.getElementById('alerts-list');
                    alertsList.innerHTML = '';
                    status.recent_alerts.slice(0, 5).forEach(alert => {
                        const alertDiv = document.createElement('div');
                        alertDiv.style.padding = '10px';
                        alertDiv.style.margin = '5px 0';
                        alertDiv.style.borderRadius = '4px';
                        alertDiv.style.backgroundColor = alert.level === 'critical' ? '#f8d7da' : 
                                                        alert.level === 'warning' ? '#fff3cd' : '#d1ecf1';
                        alertDiv.innerHTML = `
                            <strong>${alert.title}</strong><br>
                            ${alert.message}<br>
                            <small>${new Date(alert.timestamp).toLocaleString()}</small>
                        `;
                        alertsList.appendChild(alertDiv);
                    });
                }
            } catch (error) {
                console.error('대시보드 업데이트 실패:', error);
            }
        }
        
        // 성능 메트릭 업데이트
        async function updateMetrics() {
            try {
                const response = await fetch('/api/plugin-operations/metrics?type=response_times');
                const data = await response.json();
                
                if (data.status === 'success' && data.data.response_times) {
                    const times = data.data.response_times;
                    const labels = times.map((_, i) => i + 1);
                    
                    responseChart.data.labels = labels;
                    responseChart.data.datasets[0].data = times;
                    responseChart.update();
                }
            } catch (error) {
                console.error('메트릭 업데이트 실패:', error);
            }
        }
        
        // 초기 로드 및 주기적 업데이트
        updateDashboard();
        updateMetrics();
        
        setInterval(updateDashboard, 30000); // 30초마다 대시보드 업데이트
        setInterval(updateMetrics, 60000);   // 1분마다 메트릭 업데이트
    </script>
</body>
</html>'''
        
        with open(dashboard_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        logger.info("  [OK] 운영 대시보드 생성 완료")
        logger.info(f"  대시보드 위치: {dashboard_dir / 'index.html'}")
        
        return True
        
    except Exception as e:
        logger.error(f"운영 대시보드 생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("플러그인 운영 및 모니터링 시스템 초기화 스크립트 시작")
    
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 1. 플러그인 운영 및 모니터링 시스템 초기화
    if not init_plugin_operations():
        logger.error("플러그인 운영 및 모니터링 시스템 초기화 실패")
        return False
    
    # 2. 운영 대시보드 생성
    if not create_operations_dashboard():
        logger.error("운영 대시보드 생성 실패")
        return False
    
    # 3. API 테스트 (서버가 실행 중인 경우)
    try:
        test_plugin_operations_apis()
    except Exception as e:
        logger.warning(f"API 테스트 건너뜀 (서버가 실행되지 않음): {e}")
    
    logger.info("플러그인 운영 및 모니터링 시스템 초기화 스크립트 완료")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 