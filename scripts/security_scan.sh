#!/bin/bash

# 자동화된 보안 점검 스크립트
# - 취약점 스캔, 정책 위반 탐지, 리포트/알림
# 사용법: ./security_scan.sh [scan|report|alert]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_FILE="logs/security_scan.log"
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
            --data "{\"text\":\"[SecurityScan] $subject: $message\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || true
    fi
}

run_bandit() {
    log "Bandit 보안 스캔 시작"
    bandit -r . -f json -o bandit-report.json || true
    local issues=$(jq '.results | length' bandit-report.json)
    log "Bandit 스캔 결과: $issues 건의 이슈 발견"
    if [ "$issues" -gt 0 ]; then
        send_alert "Bandit 취약점 발견" "$issues 건의 보안 이슈가 발견되었습니다."
    fi
}

run_safety() {
    log "Safety 의존성 취약점 검사 시작"
    safety check --json --output safety-report.json || true
    local issues=$(jq '.vulnerabilities | length' safety-report.json)
    log "Safety 스캔 결과: $issues 건의 취약점 발견"
    if [ "$issues" -gt 0 ]; then
        send_alert "Safety 취약점 발견" "$issues 건의 의존성 취약점이 발견되었습니다."
    fi
}

run_custom_policy() {
    log "정책 위반 탐지 시작"
    # 예시: 환경변수/설정 파일 내 민감정보 노출 탐지
    local secrets=$(grep -r -E 'AKIA[0-9A-Z]{16}|aws_secret_access_key|password|secret' config/ .env* 2>/dev/null | wc -l)
    if [ "$secrets" -gt 0 ]; then
        log "${RED}[WARNING]${NC} 민감정보 노출 가능성: $secrets 건"
        send_alert "정책 위반(민감정보)" "$secrets 건의 민감정보 노출 가능성이 탐지되었습니다."
    else
        log "정책 위반 없음"
    fi
}

show_report() {
    log "보안 점검 리포트 요약"
    echo "--- Bandit ---"
    jq '.' bandit-report.json 2>/dev/null | head -30
    echo "--- Safety ---"
    jq '.' safety-report.json 2>/dev/null | head -30
    echo "--- 로그 ---"
    tail -20 "$LOG_FILE"
}

main() {
    action=${1:-scan}
    case $action in
        scan)
            run_bandit
            run_safety
            run_custom_policy
            ;;
        report)
            show_report
            ;;
        alert)
            send_alert "수동 알림 테스트" "보안 점검 알림 테스트입니다."
            ;;
        *)
            echo "Usage: $0 [scan|report|alert]"
            exit 1
            ;;
    esac
}

main "$@" 