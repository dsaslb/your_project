#!/bin/bash

# Your Program 운영 자동화 스크립트
# 사용법: ./operations.sh [action] [options]

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
PROJECT_NAME="your_program"
LOG_DIR="logs"
MONITORING_DIR="monitoring"
ALERT_EMAIL="admin@yourprogram.com"

# 로그 로테이션
rotate_logs() {
    log_info "Rotating logs..."
    
    local date_suffix=$(date +%Y%m%d_%H%M%S)
    
    # 애플리케이션 로그 로테이션
    if [ -f "$LOG_DIR/app.log" ]; then
        mv "$LOG_DIR/app.log" "$LOG_DIR/app.log.$date_suffix"
        touch "$LOG_DIR/app.log"
        log_success "Application log rotated"
    fi
    
    # Nginx 로그 로테이션
    if [ -f "$LOG_DIR/nginx_access.log" ]; then
        mv "$LOG_DIR/nginx_access.log" "$LOG_DIR/nginx_access.log.$date_suffix"
        touch "$LOG_DIR/nginx_access.log"
        log_success "Nginx access log rotated"
    fi
    
    if [ -f "$LOG_DIR/nginx_error.log" ]; then
        mv "$LOG_DIR/nginx_error.log" "$LOG_DIR/nginx_error.log.$date_suffix"
        touch "$LOG_DIR/nginx_error.log"
        log_success "Nginx error log rotated"
    fi
    
    # 오래된 로그 파일 압축
    find "$LOG_DIR" -name "*.log.*" -mtime +1 -exec gzip {} \; 2>/dev/null || true
    
    # 오래된 로그 파일 삭제 (30일)
    find "$LOG_DIR" -name "*.log.*" -mtime +30 -delete 2>/dev/null || true
    
    log_success "Log rotation completed"
}

# 시스템 모니터링
monitor_system() {
    log_info "Monitoring system resources..."
    
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    # 임계값 체크
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        log_warning "High CPU usage: ${cpu_usage}%"
        send_alert "High CPU Usage" "CPU usage is ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_usage > 85" | bc -l) )); then
        log_warning "High memory usage: ${memory_usage}%"
        send_alert "High Memory Usage" "Memory usage is ${memory_usage}%"
    fi
    
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "High disk usage: ${disk_usage}%"
        send_alert "High Disk Usage" "Disk usage is ${disk_usage}%"
    fi
    
    log_success "System monitoring completed"
}

# 애플리케이션 모니터링
monitor_application() {
    log_info "Monitoring application health..."
    
    local health_url="https://yourprogram.com/health"
    local status_url="https://yourprogram.com/api/status"
    
    # 헬스체크
    if ! curl -f -s "$health_url" > /dev/null; then
        log_error "Application health check failed"
        send_alert "Application Down" "Health check failed for $health_url"
        return 1
    fi
    
    # 응답 시간 체크
    local response_time=$(curl -w "%{time_total}" -s -o /dev/null "$status_url")
    
    if (( $(echo "$response_time > 5.0" | bc -l) )); then
        log_warning "Slow response time: ${response_time}s"
        send_alert "Slow Response Time" "Response time is ${response_time}s"
    fi
    
    # 에러 로그 체크
    local error_count=$(grep -c "ERROR" "$LOG_DIR/app.log" 2>/dev/null || echo "0")
    
    if [ "$error_count" -gt 100 ]; then
        log_warning "High error count: $error_count"
        send_alert "High Error Count" "Found $error_count errors in logs"
    fi
    
    log_success "Application monitoring completed"
}

# 데이터베이스 모니터링
monitor_database() {
    log_info "Monitoring database..."
    
    # 연결 수 체크
    local connections=$(docker-compose exec -T db psql -U your_program -d your_program -c "SELECT count(*) FROM pg_stat_activity;" -t 2>/dev/null | tr -d ' ')
    
    if [ "$connections" -gt 80 ]; then
        log_warning "High database connections: $connections"
        send_alert "High Database Connections" "Database has $connections active connections"
    fi
    
    # 느린 쿼리 체크
    local slow_queries=$(docker-compose exec -T db psql -U your_program -d your_program -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '30 seconds';" -t 2>/dev/null | tr -d ' ')
    
    if [ "$slow_queries" -gt 0 ]; then
        log_warning "Slow queries detected: $slow_queries"
        send_alert "Slow Database Queries" "Found $slow_queries slow queries"
    fi
    
    log_success "Database monitoring completed"
}

# Redis 모니터링
monitor_redis() {
    log_info "Monitoring Redis..."
    
    # 메모리 사용량 체크
    local memory_usage=$(docker-compose exec -T redis redis-cli --raw info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
    local max_memory=$(docker-compose exec -T redis redis-cli --raw config get maxmemory | tail -1)
    
    if [ -n "$max_memory" ] && [ "$max_memory" != "0" ]; then
        local usage_percent=$(docker-compose exec -T redis redis-cli --raw info memory | grep "used_memory_percent" | cut -d: -f2 | tr -d '\r')
        
        if [ "$usage_percent" -gt 85 ]; then
            log_warning "High Redis memory usage: ${usage_percent}%"
            send_alert "High Redis Memory Usage" "Redis memory usage is ${usage_percent}%"
        fi
    fi
    
    log_success "Redis monitoring completed"
}

# 보안 모니터링
monitor_security() {
    log_info "Monitoring security events..."
    
    # 로그인 실패 체크
    local failed_logins=$(grep -c "LOGIN_FAILED" "$LOG_DIR/app.log" 2>/dev/null || echo "0")
    
    if [ "$failed_logins" -gt 50 ]; then
        log_warning "High login failure rate: $failed_logins"
        send_alert "High Login Failures" "Detected $failed_logins failed login attempts"
    fi
    
    # 의심스러운 IP 체크
    local suspicious_ips=$(grep "ERROR\|WARNING" "$LOG_DIR/app.log" 2>/dev/null | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort | uniq -c | sort -nr | head -5)
    
    if [ -n "$suspicious_ips" ]; then
        log_warning "Suspicious IP activity detected"
        send_alert "Suspicious IP Activity" "Detected suspicious activity from IPs: $suspicious_ips"
    fi
    
    log_success "Security monitoring completed"
}

# 백업 모니터링
monitor_backups() {
    log_info "Monitoring backups..."
    
    # 최신 백업 확인
    local latest_backup=$(find backups/ -name "*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -n "$latest_backup" ]; then
        local backup_age=$(( $(date +%s) - $(stat -c %Y "$latest_backup") ))
        local backup_age_hours=$(( backup_age / 3600 ))
        
        if [ "$backup_age_hours" -gt 24 ]; then
            log_warning "Backup is old: ${backup_age_hours} hours"
            send_alert "Old Backup" "Latest backup is ${backup_age_hours} hours old"
        fi
    else
        log_error "No backups found"
        send_alert "No Backups" "No database backups found"
    fi
    
    log_success "Backup monitoring completed"
}

# 알림 전송
send_alert() {
    local subject="$1"
    local message="$2"
    
    log_info "Sending alert: $subject"
    
    # 이메일 알림
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "[$PROJECT_NAME] $subject" "$ALERT_EMAIL" 2>/dev/null || log_warning "Email alert failed"
    fi
    
    # Slack 알림 (예시)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$PROJECT_NAME] $subject: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || log_warning "Slack alert failed"
    fi
}

# 성능 최적화
optimize_performance() {
    log_info "Running performance optimization..."
    
    # 데이터베이스 최적화
    docker-compose exec -T db psql -U your_program -d your_program -c "VACUUM ANALYZE;" 2>/dev/null || log_warning "Database optimization failed"
    
    # Redis 메모리 최적화
    docker-compose exec -T redis redis-cli --raw FLUSHDB 2>/dev/null || log_warning "Redis optimization failed"
    
    # 로그 파일 정리
    find "$LOG_DIR" -name "*.log.*" -size +100M -delete 2>/dev/null || true
    
    log_success "Performance optimization completed"
}

# 시스템 정리
cleanup_system() {
    log_info "Running system cleanup..."
    
    # Docker 정리
    docker system prune -f 2>/dev/null || log_warning "Docker cleanup failed"
    
    # 임시 파일 정리
    find /tmp -name "*.tmp" -mtime +7 -delete 2>/dev/null || true
    
    # 오래된 로그 파일 정리
    find "$LOG_DIR" -name "*.log.*" -mtime +30 -delete 2>/dev/null || true
    
    log_success "System cleanup completed"
}

# 상태 리포트 생성
generate_report() {
    log_info "Generating status report..."
    
    local report_file="$MONITORING_DIR/status_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=== Your Program Status Report ==="
        echo "Generated: $(date)"
        echo ""
        
        echo "=== System Resources ==="
        echo "CPU Usage: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)%"
        echo "Memory Usage: $(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')%"
        echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        
        echo "=== Application Status ==="
        if curl -f -s "https://yourprogram.com/health" > /dev/null; then
            echo "Application: RUNNING"
        else
            echo "Application: DOWN"
        fi
        echo ""
        
        echo "=== Database Status ==="
        local db_connections=$(docker-compose exec -T db psql -U your_program -d your_program -c "SELECT count(*) FROM pg_stat_activity;" -t 2>/dev/null | tr -d ' ' || echo "UNKNOWN")
        echo "Active Connections: $db_connections"
        echo ""
        
        echo "=== Recent Errors ==="
        tail -20 "$LOG_DIR/app.log" 2>/dev/null | grep "ERROR" || echo "No recent errors"
        echo ""
        
        echo "=== Backup Status ==="
        local latest_backup=$(find backups/ -name "*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "No backups found")
        echo "Latest Backup: $latest_backup"
        
    } > "$report_file"
    
    log_success "Status report generated: $report_file"
}

# 장애 감지 및 자동 복구
recover_services() {
    log_info "장애 감지 및 자동 복구 실행..."
    bash ./scripts/auto_recover.sh check
}

# 메인 함수
main() {
    local action=$1
    shift
    
    case $action in
        "rotate-logs")
            rotate_logs
            ;;
        "monitor-system")
            monitor_system
            ;;
        "monitor-app")
            monitor_application
            ;;
        "monitor-db")
            monitor_database
            ;;
        "monitor-redis")
            monitor_redis
            ;;
        "monitor-security")
            monitor_security
            ;;
        "monitor-backups")
            monitor_backups
            ;;
        "monitor-all")
            monitor_system
            monitor_application
            monitor_database
            monitor_redis
            monitor_security
            monitor_backups
            ;;
        "optimize")
            optimize_performance
            ;;
        "cleanup")
            cleanup_system
            ;;
        "report")
            generate_report
            ;;
        "alert")
            send_alert "$1" "$2"
            ;;
        "recover")
            recover_services
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Usage: $0 [rotate-logs|monitor-system|monitor-app|monitor-db|monitor-redis|monitor-security|monitor-backups|monitor-all|optimize|cleanup|report|alert|recover] [options]"
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@" 