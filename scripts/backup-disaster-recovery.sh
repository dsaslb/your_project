#!/bin/bash

# Your Program 백업 및 재해 복구 스크립트
# 사용법: ./scripts/backup-disaster-recovery.sh [action] [target]
# action: backup, restore, verify, test-recovery (기본값: backup)
# target: database, files, all (기본값: all)

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
ACTION=${1:-backup}
TARGET=${2:-all}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_ROOT="$PROJECT_ROOT/backups"
DISASTER_RECOVERY_ROOT="$PROJECT_ROOT/disaster-recovery"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="backup_${TARGET}_${TIMESTAMP}"

# 클라우드 설정 (AWS S3 예시)
S3_BUCKET=${S3_BUCKET:-"your-program-backups"}
S3_REGION=${S3_REGION:-"us-east-1"}
CLOUD_PROVIDER=${CLOUD_PROVIDER:-"aws"}

# 데이터베이스 백업
backup_database() {
    log_info "Creating database backup..."
    
    local backup_dir="$BACKUP_ROOT/database/$BACKUP_NAME"
    mkdir -p "$backup_dir"
    
    # PostgreSQL 백업
    log_info "Backing up PostgreSQL databases..."
    
    # 메인 데이터베이스 백업
    docker-compose exec -T postgres pg_dump -U your_program your_program > "$backup_dir/main_database.sql" 2>/dev/null || {
        log_error "Failed to backup main database"
        return 1
    }
    
    # AI 데이터베이스 백업
    docker-compose exec -T postgres pg_dump -U your_program_ai your_program_ai > "$backup_dir/ai_database.sql" 2>/dev/null || {
        log_error "Failed to backup AI database"
        return 1
    }
    
    # 데이터베이스 설정 백업
    docker-compose exec -T postgres pg_dumpall -U your_program --globals-only > "$backup_dir/globals.sql" 2>/dev/null || {
        log_warning "Failed to backup global settings"
    }
    
    # 백업 메타데이터 생성
    cat > "$backup_dir/backup_metadata.json" << EOF
{
  "backup_type": "database",
  "timestamp": "$(date -Iseconds)",
  "databases": ["your_program", "your_program_ai"],
  "backup_size": "$(du -sh $backup_dir | cut -f1)",
  "checksum": "$(find $backup_dir -type f -name "*.sql" -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)"
}
EOF
    
    # 압축
    tar -czf "$backup_dir.tar.gz" -C "$BACKUP_ROOT/database" "$BACKUP_NAME"
    rm -rf "$backup_dir"
    
    log_success "Database backup created: $backup_dir.tar.gz"
}

# 파일 백업
backup_files() {
    log_info "Creating file backup..."
    
    local backup_dir="$BACKUP_ROOT/files/$BACKUP_NAME"
    mkdir -p "$backup_dir"
    
    # 설정 파일 백업
    log_info "Backing up configuration files..."
    
    # 환경 변수 파일
    if [ -f "$PROJECT_ROOT/.env" ]; then
        cp "$PROJECT_ROOT/.env" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_ROOT/.env.production" ]; then
        cp "$PROJECT_ROOT/.env.production" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_ROOT/.env.staging" ]; then
        cp "$PROJECT_ROOT/.env.staging" "$backup_dir/"
    fi
    
    # Docker 설정
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        cp "$PROJECT_ROOT/docker-compose.yml" "$backup_dir/"
    fi
    
    # Nginx 설정
    if [ -d "$PROJECT_ROOT/nginx" ]; then
        cp -r "$PROJECT_ROOT/nginx" "$backup_dir/"
    fi
    
    # SSL 인증서
    if [ -d "$PROJECT_ROOT/ssl" ]; then
        cp -r "$PROJECT_ROOT/ssl" "$backup_dir/"
    fi
    
    # 업로드 파일
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        log_info "Backing up upload files..."
        tar -czf "$backup_dir/uploads.tar.gz" -C "$PROJECT_ROOT" uploads/
    fi
    
    # 로그 파일
    if [ -d "$PROJECT_ROOT/logs" ]; then
        log_info "Backing up log files..."
        tar -czf "$backup_dir/logs.tar.gz" -C "$PROJECT_ROOT" logs/
    fi
    
    # 백업 메타데이터 생성
    cat > "$backup_dir/backup_metadata.json" << EOF
{
  "backup_type": "files",
  "timestamp": "$(date -Iseconds)",
  "files_included": ["config", "uploads", "logs"],
  "backup_size": "$(du -sh $backup_dir | cut -f1)",
  "checksum": "$(find $backup_dir -type f -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)"
}
EOF
    
    # 압축
    tar -czf "$backup_dir.tar.gz" -C "$BACKUP_ROOT/files" "$BACKUP_NAME"
    rm -rf "$backup_dir"
    
    log_success "File backup created: $backup_dir.tar.gz"
}

# 클라우드 백업
backup_to_cloud() {
    log_info "Uploading backup to cloud storage..."
    
    local backup_file="$1"
    
    case $CLOUD_PROVIDER in
        "aws")
            if command -v aws &> /dev/null; then
                aws s3 cp "$backup_file" "s3://$S3_BUCKET/$(basename $backup_file)" --region "$S3_REGION" || {
                    log_error "Failed to upload to S3"
                    return 1
                }
                log_success "Backup uploaded to S3: s3://$S3_BUCKET/$(basename $backup_file)"
            else
                log_warning "AWS CLI not available, skipping cloud backup"
            fi
            ;;
        "gcp")
            if command -v gsutil &> /dev/null; then
                gsutil cp "$backup_file" "gs://$S3_BUCKET/$(basename $backup_file)" || {
                    log_error "Failed to upload to GCS"
                    return 1
                }
                log_success "Backup uploaded to GCS: gs://$S3_BUCKET/$(basename $backup_file)"
            else
                log_warning "gsutil not available, skipping cloud backup"
            fi
            ;;
        *)
            log_warning "Unknown cloud provider: $CLOUD_PROVIDER"
            ;;
    esac
}

# 백업 검증
verify_backup() {
    log_info "Verifying backup integrity..."
    
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # 압축 파일 검증
    if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
        log_error "Backup file is corrupted: $backup_file"
        return 1
    fi
    
    # 메타데이터 확인
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir" --strip-components=1
    
    if [ -f "$temp_dir/backup_metadata.json" ]; then
        log_info "Backup metadata found:"
        cat "$temp_dir/backup_metadata.json" | jq '.' 2>/dev/null || {
            log_warning "Failed to parse backup metadata"
        }
    fi
    
    rm -rf "$temp_dir"
    
    log_success "Backup verification passed: $backup_file"
}

# 데이터베이스 복원
restore_database() {
    log_info "Restoring database from backup..."
    
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # 백업 검증
    verify_backup "$backup_file"
    
    # 임시 디렉토리 생성
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir" --strip-components=1
    
    # 서비스 중지
    log_info "Stopping services..."
    docker-compose down
    
    # 데이터베이스 복원
    log_info "Restoring databases..."
    
    if [ -f "$temp_dir/main_database.sql" ]; then
        docker-compose up -d postgres
        sleep 10
        
        docker-compose exec -T postgres psql -U your_program -d your_program -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        docker-compose exec -T postgres psql -U your_program your_program < "$temp_dir/main_database.sql"
        
        log_success "Main database restored"
    fi
    
    if [ -f "$temp_dir/ai_database.sql" ]; then
        docker-compose exec -T postgres psql -U your_program_ai -d your_program_ai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        docker-compose exec -T postgres psql -U your_program_ai your_program_ai < "$temp_dir/ai_database.sql"
        
        log_success "AI database restored"
    fi
    
    # 글로벌 설정 복원
    if [ -f "$temp_dir/globals.sql" ]; then
        docker-compose exec -T postgres psql -U your_program < "$temp_dir/globals.sql"
        log_success "Global settings restored"
    fi
    
    # 서비스 재시작
    docker-compose up -d
    
    # 정리
    rm -rf "$temp_dir"
    
    log_success "Database restoration completed"
}

# 파일 복원
restore_files() {
    log_info "Restoring files from backup..."
    
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # 백업 검증
    verify_backup "$backup_file"
    
    # 임시 디렉토리 생성
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir" --strip-components=1
    
    # 설정 파일 복원
    if [ -f "$temp_dir/.env" ]; then
        cp "$temp_dir/.env" "$PROJECT_ROOT/"
        log_success "Environment file restored"
    fi
    
    if [ -f "$temp_dir/.env.production" ]; then
        cp "$temp_dir/.env.production" "$PROJECT_ROOT/"
        log_success "Production environment file restored"
    fi
    
    if [ -f "$temp_dir/.env.staging" ]; then
        cp "$temp_dir/.env.staging" "$PROJECT_ROOT/"
        log_success "Staging environment file restored"
    fi
    
    if [ -f "$temp_dir/docker-compose.yml" ]; then
        cp "$temp_dir/docker-compose.yml" "$PROJECT_ROOT/"
        log_success "Docker Compose file restored"
    fi
    
    # Nginx 설정 복원
    if [ -d "$temp_dir/nginx" ]; then
        cp -r "$temp_dir/nginx" "$PROJECT_ROOT/"
        log_success "Nginx configuration restored"
    fi
    
    # SSL 인증서 복원
    if [ -d "$temp_dir/ssl" ]; then
        cp -r "$temp_dir/ssl" "$PROJECT_ROOT/"
        log_success "SSL certificates restored"
    fi
    
    # 업로드 파일 복원
    if [ -f "$temp_dir/uploads.tar.gz" ]; then
        tar -xzf "$temp_dir/uploads.tar.gz" -C "$PROJECT_ROOT"
        log_success "Upload files restored"
    fi
    
    # 로그 파일 복원
    if [ -f "$temp_dir/logs.tar.gz" ]; then
        tar -xzf "$temp_dir/logs.tar.gz" -C "$PROJECT_ROOT"
        log_success "Log files restored"
    fi
    
    # 정리
    rm -rf "$temp_dir"
    
    log_success "File restoration completed"
}

# 재해 복구 테스트
test_disaster_recovery() {
    log_info "Testing disaster recovery procedures..."
    
    # 테스트 환경 생성
    local test_env="$DISASTER_RECOVERY_ROOT/test_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$test_env"
    
    # 최신 백업 찾기
    local latest_backup=$(find "$BACKUP_ROOT" -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -z "$latest_backup" ]; then
        log_error "No backup found for testing"
        return 1
    fi
    
    log_info "Using backup for testing: $latest_backup"
    
    # 테스트 환경에 복원
    cd "$test_env"
    
    # 백업 복원 테스트
    if [[ "$latest_backup" == *"database"* ]]; then
        log_info "Testing database recovery..."
        restore_database "$latest_backup"
    elif [[ "$latest_backup" == *"files"* ]]; then
        log_info "Testing file recovery..."
        restore_files "$latest_backup"
    fi
    
    # 복원 검증
    log_info "Verifying recovery..."
    
    # 서비스 상태 확인
    if docker-compose ps | grep -q "Up"; then
        log_success "Services are running after recovery"
    else
        log_error "Services failed to start after recovery"
        return 1
    fi
    
    # 데이터베이스 연결 확인
    if docker-compose exec -T postgres pg_isready -U your_program; then
        log_success "Database connection verified"
    else
        log_error "Database connection failed"
        return 1
    fi
    
    # API 엔드포인트 확인
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # 테스트 환경 정리
    cd "$PROJECT_ROOT"
    docker-compose down
    rm -rf "$test_env"
    
    log_success "Disaster recovery test completed successfully"
}

# 백업 정리
cleanup_old_backups() {
    log_info "Cleaning up old backups..."
    
    # 30일 이상 된 백업 삭제
    find "$BACKUP_ROOT" -name "*.tar.gz" -type f -mtime +30 -delete
    
    # 클라우드 백업 정리
    case $CLOUD_PROVIDER in
        "aws")
            if command -v aws &> /dev/null; then
                aws s3 ls "s3://$S3_BUCKET/" | awk '{print $4}' | while read file; do
                    # 30일 이상 된 파일 삭제
                    aws s3 ls "s3://$S3_BUCKET/$file" --query 'Contents[0].LastModified' --output text | xargs -I {} sh -c '
                        if [ $(date -d "{}" +%s) -lt $(date -d "30 days ago" +%s) ]; then
                            aws s3 rm "s3://$S3_BUCKET/$file"
                        fi
                    '
                done
            fi
            ;;
    esac
    
    log_success "Backup cleanup completed"
}

# 백업 상태 보고
generate_backup_report() {
    log_info "Generating backup report..."
    
    local report_file="$BACKUP_ROOT/backup_report_$(date +%Y%m%d).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Your Program Backup Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Your Program Backup Report</h1>
    <p><strong>Generated:</strong> $(date)</p>
    
    <h2>Recent Backups</h2>
    <table>
        <tr>
            <th>Backup Name</th>
            <th>Type</th>
            <th>Size</th>
            <th>Date</th>
            <th>Status</th>
        </tr>
EOF

    # 최근 백업 목록
    find "$BACKUP_ROOT" -name "*.tar.gz" -type f -printf '%T@ %p %s\n' | sort -n | tail -10 | while read timestamp file size; do
        filename=$(basename "$file")
        date=$(date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S')
        size_mb=$(echo "scale=2; $size/1024/1024" | bc)
        
        if [[ "$filename" == *"database"* ]]; then
            type="Database"
        elif [[ "$filename" == *"files"* ]]; then
            type="Files"
        else
            type="Unknown"
        fi
        
        echo "        <tr>"
        echo "            <td>$filename</td>"
        echo "            <td>$type</td>"
        echo "            <td>${size_mb}MB</td>"
        echo "            <td>$date</td>"
        echo "            <td class=\"success\">✓ Available</td>"
        echo "        </tr>"
    done >> "$report_file"
    
    cat >> "$report_file" << EOF
    </table>
    
    <h2>Backup Statistics</h2>
    <ul>
        <li>Total backups: $(find $BACKUP_ROOT -name "*.tar.gz" | wc -l)</li>
        <li>Total size: $(du -sh $BACKUP_ROOT | cut -f1)</li>
        <li>Oldest backup: $(find $BACKUP_ROOT -name "*.tar.gz" -printf '%T@ %p\n' | sort -n | head -1 | cut -d' ' -f2- | xargs basename 2>/dev/null || echo "None")</li>
        <li>Latest backup: $(find $BACKUP_ROOT -name "*.tar.gz" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2- | xargs basename 2>/dev/null || echo "None")</li>
    </ul>
</body>
</html>
EOF

    log_success "Backup report generated: $report_file"
}

# 메인 로직
main() {
    log_info "Your Program Backup & Disaster Recovery"
    log_info "Action: $ACTION"
    log_info "Target: $TARGET"
    log_info "Timestamp: $TIMESTAMP"
    
    # 디렉토리 생성
    mkdir -p "$BACKUP_ROOT/database" "$BACKUP_ROOT/files" "$DISASTER_RECOVERY_ROOT"
    
    case $ACTION in
        "backup")
            case $TARGET in
                "database")
                    backup_database
                    backup_to_cloud "$BACKUP_ROOT/database/$BACKUP_NAME.tar.gz"
                    ;;
                "files")
                    backup_files
                    backup_to_cloud "$BACKUP_ROOT/files/$BACKUP_NAME.tar.gz"
                    ;;
                "all")
                    backup_database
                    backup_files
                    backup_to_cloud "$BACKUP_ROOT/database/$BACKUP_NAME.tar.gz"
                    backup_to_cloud "$BACKUP_ROOT/files/$BACKUP_NAME.tar.gz"
                    ;;
                *)
                    log_error "Invalid target: $TARGET"
                    exit 1
                    ;;
            esac
            
            # 백업 검증
            if [ "$TARGET" = "database" ] || [ "$TARGET" = "all" ]; then
                verify_backup "$BACKUP_ROOT/database/$BACKUP_NAME.tar.gz"
            fi
            if [ "$TARGET" = "files" ] || [ "$TARGET" = "all" ]; then
                verify_backup "$BACKUP_ROOT/files/$BACKUP_NAME.tar.gz"
            fi
            
            # 백업 정리
            cleanup_old_backups
            
            # 보고서 생성
            generate_backup_report
            ;;
            
        "restore")
            # 최신 백업 찾기
            local latest_backup=$(find "$BACKUP_ROOT" -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
            
            if [ -z "$latest_backup" ]; then
                log_error "No backup found for restoration"
                exit 1
            fi
            
            case $TARGET in
                "database")
                    restore_database "$latest_backup"
                    ;;
                "files")
                    restore_files "$latest_backup"
                    ;;
                "all")
                    restore_database "$latest_backup"
                    restore_files "$latest_backup"
                    ;;
                *)
                    log_error "Invalid target: $TARGET"
                    exit 1
                    ;;
            esac
            ;;
            
        "verify")
            # 모든 백업 검증
            find "$BACKUP_ROOT" -name "*.tar.gz" -type f | while read backup; do
                verify_backup "$backup"
            done
            ;;
            
        "test-recovery")
            test_disaster_recovery
            ;;
            
        *)
            log_error "Invalid action: $ACTION"
            exit 1
            ;;
    esac
    
    log_success "Backup and disaster recovery process completed"
}

# 스크립트 실행
main "$@" 