#!/bin/bash

# Your Program 다중 데이터베이스 초기화 스크립트
# PostgreSQL 컨테이너에서 실행됨

set -e

# 환경 변수
POSTGRES_DB=${POSTGRES_DB:-your_program}
POSTGRES_USER=${POSTGRES_USER:-your_program}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}
POSTGRES_MULTIPLE_DATABASES=${POSTGRES_MULTIPLE_DATABASES:-your_program,your_program_ai}

# 로그 함수
log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_error() {
    echo "[ERROR] $1"
}

# 데이터베이스 생성 함수
create_database() {
    local database=$1
    local user=$2
    local password=$3
    
    log_info "Creating database: $database"
    
    # 데이터베이스 존재 여부 확인
    if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$database"; then
        log_info "Database $database already exists"
    else
        # 데이터베이스 생성
        createdb -U "$POSTGRES_USER" "$database"
        log_success "Database $database created successfully"
    fi
    
    # 사용자 생성 (필요한 경우)
    if [ "$user" != "$POSTGRES_USER" ]; then
        log_info "Creating user: $user"
        
        # 사용자 존재 여부 확인
        if psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$user'" | grep -q 1; then
            log_info "User $user already exists"
        else
            # 사용자 생성
            psql -U "$POSTGRES_USER" -c "CREATE USER $user WITH PASSWORD '$password';"
            log_success "User $user created successfully"
        fi
        
        # 권한 부여
        psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $database TO $user;"
        psql -U "$POSTGRES_USER" -c "ALTER DATABASE $database OWNER TO $user;"
        log_success "Privileges granted to $user on $database"
    fi
}

# 확장 설치 함수
install_extensions() {
    local database=$1
    
    log_info "Installing extensions for database: $database"
    
    # PostgreSQL 확장 설치
    psql -U "$POSTGRES_USER" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
    psql -U "$POSTGRES_USER" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"
    psql -U "$POSTGRES_USER" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";"
    psql -U "$POSTGRES_USER" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";"
    
    # AI 데이터베이스용 추가 확장
    if [[ "$database" == *"ai"* ]]; then
        psql -U "$POSTGRES_USER" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"vector\";"
        psql -U "$POSTGRES_USER" -d "$database" -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
        log_info "AI-specific extensions installed for $database"
    fi
    
    log_success "Extensions installed for $database"
}

# 초기 테이블 생성 함수
create_initial_tables() {
    local database=$1
    
    log_info "Creating initial tables for database: $database"
    
    # 기본 시스템 테이블
    psql -U "$POSTGRES_USER" -d "$database" << EOF
-- 시스템 설정 테이블
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 로그 테이블
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    service VARCHAR(100),
    user_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 메트릭 테이블
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_system_logs_service ON system_logs(service);
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);

-- 기본 설정 데이터
INSERT INTO system_config (config_key, config_value, description) VALUES
('app_name', 'Your Program', 'Application name'),
('app_version', '1.0.0', 'Application version'),
('environment', 'production', 'Environment type'),
('maintenance_mode', 'false', 'Maintenance mode flag'),
('max_connections', '100', 'Maximum database connections'),
('session_timeout', '3600', 'Session timeout in seconds')
ON CONFLICT (config_key) DO NOTHING;
EOF
    
    log_success "Initial tables created for $database"
}

# AI 데이터베이스 전용 테이블 생성
create_ai_tables() {
    local database=$1
    
    if [[ "$database" == *"ai"* ]]; then
        log_info "Creating AI-specific tables for database: $database"
        
        psql -U "$POSTGRES_USER" -d "$database" << EOF
-- AI 모델 테이블
CREATE TABLE IF NOT EXISTS ai_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_path TEXT NOT NULL,
    parameters JSONB,
    accuracy DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 예측 결과 테이블
CREATE TABLE IF NOT EXISTS ai_predictions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES ai_models(id),
    input_data JSONB NOT NULL,
    prediction_result JSONB NOT NULL,
    confidence DOUBLE PRECISION,
    processing_time DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 학습 데이터 테이블
CREATE TABLE IF NOT EXISTS ai_training_data (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(100) NOT NULL,
    data_source VARCHAR(255),
    data_content JSONB NOT NULL,
    labels JSONB,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 성능 메트릭 테이블
CREATE TABLE IF NOT EXISTS ai_performance_metrics (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES ai_models(id),
    metric_type VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    evaluation_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_ai_predictions_model_id ON ai_predictions(model_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_created_at ON ai_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_training_data_type ON ai_training_data(data_type);
CREATE INDEX IF NOT EXISTS idx_ai_training_data_processed ON ai_training_data(is_processed);
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_model_id ON ai_performance_metrics(model_id);
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_date ON ai_performance_metrics(evaluation_date);
EOF
        
        log_success "AI-specific tables created for $database"
    fi
}

# 메인 초기화 로직
main() {
    log_info "Starting multiple database initialization..."
    
    # 데이터베이스 목록 파싱
    IFS=',' read -ra DATABASES <<< "$POSTGRES_MULTIPLE_DATABASES"
    
    for database in "${DATABASES[@]}"; do
        database=$(echo "$database" | xargs)  # 공백 제거
        
        if [ -n "$database" ]; then
            log_info "Processing database: $database"
            
            # 데이터베이스 생성
            create_database "$database" "$POSTGRES_USER" "$POSTGRES_PASSWORD"
            
            # 확장 설치
            install_extensions "$database"
            
            # 초기 테이블 생성
            create_initial_tables "$database"
            
            # AI 전용 테이블 생성
            create_ai_tables "$database"
            
            log_success "Database $database initialized successfully"
        fi
    done
    
    log_success "Multiple database initialization completed"
    
    # 초기화 완료 표시
    echo "Database initialization completed at $(date)" > /var/lib/postgresql/data/.initialized
}

# 스크립트 실행
main "$@" 