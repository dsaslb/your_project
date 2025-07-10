#!/bin/bash

# Your Program 모니터링 시스템 설정 스크립트
# 사용법: ./scripts/setup-monitoring.sh [component] [action]
# component: prometheus, grafana, alertmanager, all (기본값: all)
# action: install, configure, start, stop, status (기본값: install)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 설정
COMPONENT=${1:-all}
ACTION=${2:-install}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITORING_ROOT="$PROJECT_ROOT/monitoring"

# Prometheus 설정
setup_prometheus() {
    log_info "Setting up Prometheus..."
    
    mkdir -p "$MONITORING_ROOT/prometheus"
    
    # Prometheus 설정 파일 생성
    cat > "$MONITORING_ROOT/prometheus/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'your-program-backend'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'your-program-ai'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'your-program-gateway'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 15s

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 15s
EOF

    # 알림 규칙 생성
    cat > "$MONITORING_ROOT/prometheus/alert_rules.yml" << 'EOF'
groups:
  - name: your-program-alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}) / node_filesystem_size_bytes{mountpoint="/"} * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage detected"
          description: "Disk usage is above 90% for more than 5 minutes"

      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100 > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for more than 2 minutes"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Service {{ $labels.job }} is down"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is above 2 seconds"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connections are above 80"

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Redis memory usage"
          description: "Redis memory usage is above 85%"
EOF

    # Prometheus Docker Compose 설정
    cat > "$MONITORING_ROOT/docker-compose.monitoring.yml" << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: your-program-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: your-program-grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: your-program-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager:/etc/alertmanager
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: your-program-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: your-program-cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    restart: unless-stopped
    networks:
      - monitoring

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: your-program-postgres-exporter
    ports:
      - "9187:9187"
    environment:
      DATA_SOURCE_NAME: "postgresql://your_program:password@postgres:5432/your_program?sslmode=disable"
    restart: unless-stopped
    networks:
      - monitoring

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: your-program-redis-exporter
    ports:
      - "9121:9121"
    environment:
      REDIS_ADDR: "redis://redis:6379"
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
EOF

    log_success "Prometheus configuration completed"
}

# Grafana 설정
setup_grafana() {
    log_info "Setting up Grafana..."
    
    mkdir -p "$MONITORING_ROOT/grafana/dashboards" "$MONITORING_ROOT/grafana/datasources"
    
    # Grafana 데이터소스 설정
    cat > "$MONITORING_ROOT/grafana/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    # Grafana 대시보드 프로비저닝 설정
    cat > "$MONITORING_ROOT/grafana/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'Your Program Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    # 기본 대시보드 복사
    if [ -f "$MONITORING_ROOT/grafana/dashboards/your-program-monitoring.json" ]; then
        log_success "Grafana dashboard found"
    else
        log_warning "Grafana dashboard not found, creating basic dashboard"
        
        cat > "$MONITORING_ROOT/grafana/dashboards/your-program-monitoring.json" << 'EOF'
{
  "dashboard": {
    "title": "Your Program Monitoring",
    "panels": [
      {
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      }
    ]
  }
}
EOF
    fi
    
    log_success "Grafana configuration completed"
}

# Alertmanager 설정
setup_alertmanager() {
    log_info "Setting up Alertmanager..."
    
    mkdir -p "$MONITORING_ROOT/alertmanager"
    
    # Alertmanager 설정 파일
    cat > "$MONITORING_ROOT/alertmanager/alertmanager.yml" << 'EOF'
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'slack-notifications'
      continue: true

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/webhook'

  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'
        send_resolved: true

templates:
  - '/etc/alertmanager/template/*.tmpl'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

    # Slack 템플릿 생성
    mkdir -p "$MONITORING_ROOT/alertmanager/template"
    
    cat > "$MONITORING_ROOT/alertmanager/template/slack.tmpl" << 'EOF'
{{ define "slack.title" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }}
{{ end }}

{{ define "slack.text" }}
{{ range .Alerts }}
*Alert:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
*Severity:* {{ .Labels.severity }}
*Instance:* {{ .Labels.instance }}
*Started:* {{ .StartsAt | since }}
{{ if .EndsAt }}*Ended:* {{ .EndsAt | since }}{{ end }}
{{ end }}
{{ end }}
EOF

    log_success "Alertmanager configuration completed"
}

# 모니터링 서비스 시작
start_monitoring() {
    log_info "Starting monitoring services..."
    
    cd "$MONITORING_ROOT"
    
    if [ -f "docker-compose.monitoring.yml" ]; then
        docker-compose -f docker-compose.monitoring.yml up -d
        
        log_info "Waiting for services to start..."
        sleep 30
        
        # 서비스 상태 확인
        local services=("prometheus" "grafana" "alertmanager" "node-exporter" "cadvisor")
        
        for service in "${services[@]}"; do
            if docker-compose -f docker-compose.monitoring.yml ps | grep -q "$service.*Up"; then
                log_success "$service is running"
            else
                log_error "$service failed to start"
            fi
        done
        
        log_info "Monitoring services started:"
        log_info "  - Prometheus: http://localhost:9090"
        log_info "  - Grafana: http://localhost:3001 (admin/admin123)"
        log_info "  - Alertmanager: http://localhost:9093"
        log_info "  - Node Exporter: http://localhost:9100"
        log_info "  - cAdvisor: http://localhost:8080"
        
    else
        log_error "docker-compose.monitoring.yml not found"
        return 1
    fi
}

# 모니터링 서비스 중지
stop_monitoring() {
    log_info "Stopping monitoring services..."
    
    cd "$MONITORING_ROOT"
    
    if [ -f "docker-compose.monitoring.yml" ]; then
        docker-compose -f docker-compose.monitoring.yml down
        log_success "Monitoring services stopped"
    else
        log_error "docker-compose.monitoring.yml not found"
        return 1
    fi
}

# 모니터링 서비스 상태 확인
status_monitoring() {
    log_info "Checking monitoring services status..."
    
    cd "$MONITORING_ROOT"
    
    if [ -f "docker-compose.monitoring.yml" ]; then
        docker-compose -f docker-compose.monitoring.yml ps
        
        # 포트 확인
        local ports=(9090 3001 9093 9100 8080)
        
        for port in "${ports[@]}"; do
            if netstat -tuln | grep -q ":$port "; then
                log_success "Port $port: LISTENING"
            else
                log_warning "Port $port: NOT LISTENING"
            fi
        done
        
    else
        log_error "docker-compose.monitoring.yml not found"
        return 1
    fi
}

# 메트릭 수집기 설정
setup_metrics_collectors() {
    log_info "Setting up metrics collectors..."
    
    # 애플리케이션 메트릭 수집기 설정
    cat > "$PROJECT_ROOT/utils/metrics_collector.py" << 'EOF'
#!/usr/bin/env python3
"""
Your Program Metrics Collector
애플리케이션 메트릭을 수집하고 Prometheus로 전송
"""

import time
import psutil
import requests
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 메트릭 정의
REQUEST_COUNT = Counter('your_program_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('your_program_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('your_program_active_users', 'Number of active users')
DATABASE_CONNECTIONS = Gauge('your_program_db_connections', 'Database connections')
REDIS_MEMORY = Gauge('your_program_redis_memory_bytes', 'Redis memory usage')
SYSTEM_CPU = Gauge('your_program_system_cpu_percent', 'System CPU usage')
SYSTEM_MEMORY = Gauge('your_program_system_memory_percent', 'System memory usage')

class MetricsCollector:
    def __init__(self, port=8000):
        self.port = port
        self.running = False
        
    def start(self):
        """메트릭 서버 시작"""
        try:
            start_http_server(self.port)
            self.running = True
            logger.info(f"Metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
            
    def collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU.set(cpu_percent)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY.set(memory.percent)
            
            logger.debug(f"System metrics collected - CPU: {cpu_percent}%, Memory: {memory.percent}%")
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            
    def collect_application_metrics(self):
        """애플리케이션 메트릭 수집"""
        try:
            # 데이터베이스 연결 수 (예시)
            # 실제 구현에서는 데이터베이스 연결 풀에서 가져옴
            DATABASE_CONNECTIONS.set(10)  # 예시 값
            
            # Redis 메모리 사용량 (예시)
            # 실제 구현에서는 Redis에서 가져옴
            REDIS_MEMORY.set(1024 * 1024 * 100)  # 100MB 예시
            
            # 활성 사용자 수 (예시)
            # 실제 구현에서는 세션/캐시에서 가져옴
            ACTIVE_USERS.set(25)  # 예시 값
            
            logger.debug("Application metrics collected")
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
            
    def run(self):
        """메트릭 수집기 실행"""
        self.start()
        
        while self.running:
            try:
                self.collect_system_metrics()
                self.collect_application_metrics()
                time.sleep(15)  # 15초마다 수집
                
            except KeyboardInterrupt:
                logger.info("Metrics collector stopped")
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(30)  # 에러 시 30초 대기

if __name__ == "__main__":
    collector = MetricsCollector()
    collector.run()
EOF

    chmod +x "$PROJECT_ROOT/utils/metrics_collector.py"
    
    log_success "Metrics collectors configured"
}

# 모니터링 대시보드 설정
setup_dashboards() {
    log_info "Setting up monitoring dashboards..."
    
    # 기본 대시보드 생성
    cat > "$MONITORING_ROOT/grafana/dashboards/your-program-overview.json" << 'EOF'
{
  "dashboard": {
    "title": "Your Program Overview",
    "panels": [
      {
        "title": "System Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{job}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      }
    ]
  }
}
EOF

    log_success "Dashboards configured"
}

# 메인 로직
main() {
    log_info "Your Program Monitoring Setup"
    log_info "Component: $COMPONENT"
    log_info "Action: $ACTION"
    
    # 모니터링 디렉토리 생성
    mkdir -p "$MONITORING_ROOT"
    
    case $ACTION in
        "install")
            case $COMPONENT in
                "prometheus")
                    setup_prometheus
                    ;;
                "grafana")
                    setup_grafana
                    ;;
                "alertmanager")
                    setup_alertmanager
                    ;;
                "all")
                    setup_prometheus
                    setup_grafana
                    setup_alertmanager
                    setup_metrics_collectors
                    setup_dashboards
                    ;;
                *)
                    log_error "Invalid component: $COMPONENT"
                    exit 1
                    ;;
            esac
            ;;
            
        "configure")
            case $COMPONENT in
                "prometheus")
                    setup_prometheus
                    ;;
                "grafana")
                    setup_grafana
                    ;;
                "alertmanager")
                    setup_alertmanager
                    ;;
                "all")
                    setup_prometheus
                    setup_grafana
                    setup_alertmanager
                    setup_dashboards
                    ;;
                *)
                    log_error "Invalid component: $COMPONENT"
                    exit 1
                    ;;
            esac
            ;;
            
        "start")
            start_monitoring
            ;;
            
        "stop")
            stop_monitoring
            ;;
            
        "status")
            status_monitoring
            ;;
            
        *)
            log_error "Invalid action: $ACTION"
            exit 1
            ;;
    esac
    
    log_success "Monitoring setup completed"
}

# 스크립트 실행
main "$@" 