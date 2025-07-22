#!/bin/bash

# 장애 자동 복구 스크립트
# - 서비스 헬스체크, 장애 감지, 자동 재시작/롤백, 알림
# 사용법: ./auto_recover.sh [check|recover|status|logs]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_FILE="logs/auto_recover.log"
ALERT_EMAIL="admin@yourprogram.com"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL}"

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local subject="$1"
    local message="$2"
    log "${YELLOW}[ALERT]${NC} $subject - $message"
    # 이메일
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    # Slack
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[AutoRecover] $subject: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
}

check_services() {
    log "서비스 헬스체크 시작"
    local failed=0
    local services=(app db redis nginx)
    for svc in "${services[@]}"; do
        health=$(docker-compose ps --services --filter "status=running" | grep "^$svc$" || true)
        if [ -z "$health" ]; then
            log "${RED}[DOWN]${NC} $svc 서비스가 중지됨"
            send_alert "서비스 다운" "$svc 서비스가 중지되었습니다. 자동 복구를 시도합니다."
            failed=1
        else
            # 헬스체크 엔드포인트 확인 (app/nginx)
            if [ "$svc" = "app" ] || [ "$svc" = "nginx" ]; then
                url="http://localhost:5000/health"
                [ "$svc" = "nginx" ] && url="http://localhost/health"
                if ! curl -f -s "$url" > /dev/null; then
                    log "${RED}[UNHEALTHY]${NC} $svc 헬스체크 실패"
                    send_alert "헬스체크 실패" "$svc 헬스체크가 실패했습니다. 자동 복구를 시도합니다."
                    failed=1
                fi
            fi
        fi
    done
    return $failed
}

recover_services() {
    log "장애 감지됨. 서비스 자동 복구 시도"
    docker-compose down --remove-orphans
    sleep 3
    docker-compose up -d
    log "서비스 재시작 완료"
    send_alert "서비스 재시작" "모든 서비스를 자동으로 재시작했습니다."
}

show_status() {
    log "서비스 상태 조회"
    docker-compose ps
}

show_logs() {
    tail -30 "$LOG_FILE"
}

main() {
    action=${1:-check}
    case $action in
        check)
            if ! check_services; then
                recover_services
            else
                log "${GREEN}[OK]${NC} 모든 서비스 정상 동작 중"
            fi
            ;;
        recover)
            recover_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        *)
            echo "Usage: $0 [check|recover|status|logs]"
            exit 1
            ;;
    esac
}

main "$@" 