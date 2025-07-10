#!/bin/bash

# Your Program 자동 스케일링 스크립트
# 사용법: ./scripts/auto-scale.sh [service] [action]
# service: backend, ai-server, frontend (기본값: all)
# action: scale-up, scale-down, check (기본값: check)

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
SERVICE=${1:-all}
ACTION=${2:-check}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 임계값 설정
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
REQUEST_THRESHOLD=1000
ERROR_RATE_THRESHOLD=5

# 현재 시간
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 메트릭 수집 함수
get_cpu_usage() {
    local service=$1
    # Prometheus에서 CPU 사용률 조회
    curl -s "http://localhost:9090/api/v1/query?query=100%20-%20(avg%20by%20(instance)%20(irate(node_cpu_seconds_total{mode=\"idle\",job=\"$service\"}[5m]))%20*%20100)" | \
    jq -r '.data.result[0].value[1] // "0"'
}

get_memory_usage() {
    local service=$1
    # Prometheus에서 메모리 사용률 조회
    curl -s "http://localhost:9090/api/v1/query?query=(node_memory_MemTotal_bytes%20-%20node_memory_MemAvailable_bytes)%20/%20node_memory_MemTotal_bytes%20*%20100" | \
    jq -r '.data.result[0].value[1] // "0"'
}

get_request_rate() {
    local service=$1
    # Prometheus에서 요청률 조회
    curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{job=\"$service\"}[5m])" | \
    jq -r '.data.result[0].value[1] // "0"'
}

get_error_rate() {
    local service=$1
    # Prometheus에서 에러률 조회
    curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{job=\"$service\",status=~\"5..\"}[5m])%20/%20rate(http_requests_total{job=\"$service\"}[5m])%20*%20100" | \
    jq -r '.data.result[0].value[1] // "0"'
}

get_current_replicas() {
    local service=$1
    # Docker Compose에서 현재 레플리카 수 조회
    docker-compose ps $service | grep -c "Up" || echo "0"
}

# 스케일링 함수
scale_service() {
    local service=$1
    local direction=$2
    local current_replicas=$(get_current_replicas $service)
    
    if [ "$direction" = "up" ]; then
        local new_replicas=$((current_replicas + 1))
        log_info "Scaling $service up from $current_replicas to $new_replicas replicas"
        
        # Docker Compose 스케일링
        docker-compose up -d --scale $service=$new_replicas
        
        # 로드 밸런서 업데이트 (Nginx)
        update_load_balancer $service $new_replicas
        
    elif [ "$direction" = "down" ]; then
        if [ $current_replicas -gt 1 ]; then
            local new_replicas=$((current_replicas - 1))
            log_info "Scaling $service down from $current_replicas to $new_replicas replicas"
            
            # Docker Compose 스케일링
            docker-compose up -d --scale $service=$new_replicas
            
            # 로드 밸런서 업데이트
            update_load_balancer $service $new_replicas
        else
            log_warning "Cannot scale down $service: minimum replicas reached"
        fi
    fi
}

# 로드 밸런서 업데이트
update_load_balancer() {
    local service=$1
    local replicas=$2
    
    # Nginx 설정 업데이트
    local nginx_conf="$PROJECT_ROOT/nginx/nginx.conf"
    local upstream_name=""
    
    case $service in
        "backend")
            upstream_name="backend_servers"
            ;;
        "ai-server")
            upstream_name="ai_servers"
            ;;
        "frontend")
            upstream_name="frontend_servers"
            ;;
    esac
    
    if [ -n "$upstream_name" ]; then
        # Nginx 설정에서 업스트림 서버 업데이트
        sed -i "s/server $service:[0-9]*/server $service:$replicas/g" $nginx_conf
        
        # Nginx 재로드
        docker-compose exec nginx nginx -s reload
        
        log_success "Load balancer updated for $service ($replicas replicas)"
    fi
}

# 헬스체크 함수
check_service_health() {
    local service=$1
    local health_url=""
    
    case $service in
        "gateway")
            health_url="http://localhost:8000/health"
            ;;
        "backend")
            health_url="http://localhost:5001/health"
            ;;
        "ai-server")
            health_url="http://localhost:8002/health"
            ;;
        "frontend")
            health_url="http://localhost:3000"
            ;;
    esac
    
    if [ -n "$health_url" ]; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" $health_url)
        if [ "$response" = "200" ]; then
            return 0
        else
            return 1
        fi
    fi
    
    return 1
}

# 메트릭 모니터링 함수
monitor_metrics() {
    local service=$1
    
    log_info "Monitoring metrics for $service..."
    
    local cpu_usage=$(get_cpu_usage $service)
    local memory_usage=$(get_memory_usage $service)
    local request_rate=$(get_request_rate $service)
    local error_rate=$(get_error_rate $service)
    local current_replicas=$(get_current_replicas $service)
    
    echo "=== $service Metrics ($TIMESTAMP) ==="
    echo "CPU Usage: ${cpu_usage}%"
    echo "Memory Usage: ${memory_usage}%"
    echo "Request Rate: ${request_rate} req/s"
    echo "Error Rate: ${error_rate}%"
    echo "Current Replicas: $current_replicas"
    echo "Health Status: $(check_service_health $service && echo "Healthy" || echo "Unhealthy")"
    echo
    
    # 스케일링 결정
    local should_scale_up=false
    local should_scale_down=false
    
    # 스케일 업 조건
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )) || \
       (( $(echo "$memory_usage > $MEMORY_THRESHOLD" | bc -l) )) || \
       (( $(echo "$request_rate > $REQUEST_THRESHOLD" | bc -l) )); then
        should_scale_up=true
    fi
    
    # 스케일 다운 조건
    if (( $(echo "$cpu_usage < 30" | bc -l) )) && \
       (( $(echo "$memory_usage < 40" | bc -l) )) && \
       (( $(echo "$request_rate < 100" | bc -l) )) && \
       [ $current_replicas -gt 1 ]; then
        should_scale_down=true
    fi
    
    # 스케일링 실행
    if [ "$should_scale_up" = true ]; then
        log_warning "High resource usage detected for $service"
        scale_service $service up
    elif [ "$should_scale_down" = true ]; then
        log_info "Low resource usage detected for $service"
        scale_service $service down
    else
        log_success "$service is running optimally"
    fi
}

# 전체 서비스 모니터링
monitor_all_services() {
    log_info "Starting auto-scaling monitoring..."
    
    local services=("gateway" "backend" "ai-server" "frontend")
    
    for service in "${services[@]}"; do
        monitor_metrics $service
        sleep 5
    done
}

# 특정 서비스 스케일링
scale_specific_service() {
    local service=$1
    local action=$2
    
    case $action in
        "scale-up")
            scale_service $service up
            ;;
        "scale-down")
            scale_service $service down
            ;;
        "check")
            monitor_metrics $service
            ;;
        *)
            log_error "Invalid action: $action"
            exit 1
            ;;
    esac
}

# 메인 로직
main() {
    log_info "Your Program Auto-Scaling System"
    log_info "Service: $SERVICE"
    log_info "Action: $ACTION"
    log_info "Timestamp: $TIMESTAMP"
    
    # Prometheus 연결 확인
    if ! curl -s http://localhost:9090/api/v1/query > /dev/null; then
        log_error "Prometheus is not accessible. Please ensure monitoring is running."
        exit 1
    fi
    
    case $SERVICE in
        "all")
            if [ "$ACTION" = "check" ]; then
                monitor_all_services
            else
                log_error "Action '$ACTION' is not supported for all services"
                exit 1
            fi
            ;;
        "gateway"|"backend"|"ai-server"|"frontend")
            scale_specific_service $SERVICE $ACTION
            ;;
        *)
            log_error "Invalid service: $SERVICE"
            log_info "Valid services: gateway, backend, ai-server, frontend, all"
            exit 1
            ;;
    esac
    
    log_success "Auto-scaling operation completed"
}

# 스크립트 실행
main "$@" 