#!/bin/bash

# Your Program 백업 및 복구 스크립트
# 사용법: ./backup.sh [backup|restore] [type] [file]

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
BACKUP_DIR="backups"
DB_NAME="your_program"
DB_USER="your_program"
DB_PASSWORD="password"
DB_HOST="db"
DB_PORT="5432"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 데이터베이스 백업
backup_database() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/database_$timestamp.sql"
    
    log_info "Creating database backup..."
    
    # PostgreSQL 백업
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$backup_file"; then
        log_success "Database backup created: $backup_file"
        
        # 백업 파일 압축
        gzip "$backup_file"
        log_success "Database backup compressed: $backup_file.gz"
        
        # 백업 파일 크기 확인
        local size=$(du -h "$backup_file.gz" | cut -f1)
        log_info "Backup size: $size"
        
        return 0
    else
        log_error "Database backup failed"
        return 1
    fi
}

# 파일 백업
backup_files() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/files_$timestamp.tar.gz"
    
    log_info "Creating files backup..."
    
    # 업로드 파일 및 설정 백업
    if tar -czf "$backup_file" uploads/ config/ nginx/ 2>/dev/null; then
        log_success "Files backup created: $backup_file"
        
        # 백업 파일 크기 확인
        local size=$(du -h "$backup_file" | cut -f1)
        log_info "Backup size: $size"
        
        return 0
    else
        log_error "Files backup failed"
        return 1
    fi
}

# 전체 백업
backup_full() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$BACKUP_DIR/full_$timestamp"
    
    log_info "Creating full backup..."
    
    mkdir -p "$backup_dir"
    
    # 데이터베이스 백업
    if backup_database; then
        # 최신 데이터베이스 백업을 전체 백업 디렉토리로 이동
        local latest_db_backup=$(ls -t "$BACKUP_DIR"/database_*.sql.gz 2>/dev/null | head -1)
        if [ -n "$latest_db_backup" ]; then
            mv "$latest_db_backup" "$backup_dir/"
        fi
    fi
    
    # 파일 백업
    if backup_files; then
        # 최신 파일 백업을 전체 백업 디렉토리로 이동
        local latest_files_backup=$(ls -t "$BACKUP_DIR"/files_*.tar.gz 2>/dev/null | head -1)
        if [ -n "$latest_files_backup" ]; then
            mv "$latest_files_backup" "$backup_dir/"
        fi
    fi
    
    # 로그 파일 백업
    if [ -d "logs" ]; then
        tar -czf "$backup_dir/logs.tar.gz" logs/ 2>/dev/null || log_warning "Logs backup failed"
    fi
    
    # 백업 메타데이터 생성
    cat > "$backup_dir/backup_info.txt" << EOF
Backup Type: Full
Created: $(date)
Environment: $(echo $ENVIRONMENT)
Version: $(echo $VERSION)
Database: $DB_NAME
Files: uploads/, config/, nginx/
EOF
    
    log_success "Full backup completed: $backup_dir"
}

# 데이터베이스 복구
restore_database() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring database from: $backup_file"
    
    # 백업 파일 압축 해제 (필요시)
    local temp_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        temp_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$temp_file"
    fi
    
    # 데이터베이스 복구
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$temp_file"; then
        log_success "Database restored successfully"
        
        # 임시 파일 정리
        if [ "$temp_file" != "$backup_file" ]; then
            rm "$temp_file"
        fi
        
        return 0
    else
        log_error "Database restore failed"
        
        # 임시 파일 정리
        if [ "$temp_file" != "$backup_file" ]; then
            rm "$temp_file"
        fi
        
        return 1
    fi
}

# 파일 복구
restore_files() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring files from: $backup_file"
    
    # 기존 파일 백업
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local current_backup="$BACKUP_DIR/current_files_$timestamp.tar.gz"
    
    if tar -czf "$current_backup" uploads/ config/ nginx/ 2>/dev/null; then
        log_info "Current files backed up to: $current_backup"
    fi
    
    # 파일 복구
    if tar -xzf "$backup_file"; then
        log_success "Files restored successfully"
        return 0
    else
        log_error "Files restore failed"
        return 1
    fi
}

# 전체 복구
restore_full() {
    local backup_dir=$1
    
    if [ ! -d "$backup_dir" ]; then
        log_error "Backup directory not found: $backup_dir"
        return 1
    fi
    
    log_info "Restoring from full backup: $backup_dir"
    
    # 데이터베이스 복구
    local db_backup=$(find "$backup_dir" -name "database_*.sql.gz" | head -1)
    if [ -n "$db_backup" ]; then
        restore_database "$db_backup"
    fi
    
    # 파일 복구
    local files_backup=$(find "$backup_dir" -name "files_*.tar.gz" | head -1)
    if [ -n "$files_backup" ]; then
        restore_files "$files_backup"
    fi
    
    # 로그 복구 (선택사항)
    local logs_backup=$(find "$backup_dir" -name "logs.tar.gz" | head -1)
    if [ -n "$logs_backup" ]; then
        log_info "Restoring logs..."
        tar -xzf "$logs_backup" 2>/dev/null || log_warning "Logs restore failed"
    fi
    
    log_success "Full restore completed"
}

# 백업 정리
cleanup_backups() {
    local days_to_keep=${1:-30}
    
    log_info "Cleaning up backups older than $days_to_keep days..."
    
    # 오래된 백업 파일 삭제
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$days_to_keep -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$days_to_keep -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "full_*" -mtime +$days_to_keep -exec rm -rf {} \; 2>/dev/null || true
    
    log_success "Backup cleanup completed"
}

# 백업 목록
list_backups() {
    log_info "Available backups:"
    
    echo "Database backups:"
    ls -lh "$BACKUP_DIR"/database_*.sql.gz 2>/dev/null || echo "No database backups found"
    
    echo -e "\nFile backups:"
    ls -lh "$BACKUP_DIR"/files_*.tar.gz 2>/dev/null || echo "No file backups found"
    
    echo -e "\nFull backups:"
    ls -ld "$BACKUP_DIR"/full_* 2>/dev/null || echo "No full backups found"
}

# 백업 검증
verify_backup() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Verifying backup: $backup_file"
    
    # 파일 무결성 검사
    if [[ "$backup_file" == *.gz ]]; then
        if gzip -t "$backup_file"; then
            log_success "Backup file integrity verified"
        else
            log_error "Backup file is corrupted"
            return 1
        fi
    fi
    
    # 데이터베이스 백업인 경우 스키마 검사
    if [[ "$backup_file" == *database* ]]; then
        local temp_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$temp_file"
        
        # 테이블 목록 확인
        local table_count=$(grep -c "CREATE TABLE" "$temp_file" || echo "0")
        log_info "Backup contains $table_count tables"
        
        rm "$temp_file"
    fi
    
    return 0
}

# 메인 함수
main() {
    local action=$1
    local type=$2
    local file=$3
    
    case $action in
        "backup")
            case $type in
                "database")
                    backup_database
                    ;;
                "files")
                    backup_files
                    ;;
                "full")
                    backup_full
                    ;;
                *)
                    log_error "Unknown backup type: $type"
                    echo "Usage: $0 backup [database|files|full]"
                    exit 1
                    ;;
            esac
            ;;
        "restore")
            case $type in
                "database")
                    restore_database "$file"
                    ;;
                "files")
                    restore_files "$file"
                    ;;
                "full")
                    restore_full "$file"
                    ;;
                *)
                    log_error "Unknown restore type: $type"
                    echo "Usage: $0 restore [database|files|full] <backup_file>"
                    exit 1
                    ;;
            esac
            ;;
        "list")
            list_backups
            ;;
        "cleanup")
            cleanup_backups "$type"
            ;;
        "verify")
            verify_backup "$type"
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Usage: $0 [backup|restore|list|cleanup|verify] [type] [file]"
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@" 