#!/bin/bash

# Your Program 보안 강화 스크립트
# 사용법: ./scripts/security-hardening.sh [target] [action]
# target: system, network, application, database, all (기본값: all)
# action: scan, harden, audit (기본값: harden)

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
TARGET=${1:-all}
ACTION=${2:-harden}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECURITY_LOG="$PROJECT_ROOT/logs/security_${TARGET}_$(date +%Y%m%d_%H%M%S).log"

# 시스템 보안 강화
harden_system() {
    log_info "Hardening system security..."
    
    # 방화벽 설정
    log_info "Configuring firewall..."
    
    # UFW 방화벽 설정 (Ubuntu/Debian)
    if command -v ufw &> /dev/null; then
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        
        # 필요한 포트만 허용
        ufw allow 22/tcp    # SSH
        ufw allow 80/tcp    # HTTP
        ufw allow 443/tcp   # HTTPS
        ufw allow 8000/tcp  # API Gateway
        ufw allow 5001/tcp  # Backend
        ufw allow 8002/tcp  # AI Server
        ufw allow 3000/tcp  # Frontend
        ufw allow 5432/tcp  # PostgreSQL
        ufw allow 6379/tcp  # Redis
        
        ufw --force enable
        log_success "UFW firewall configured"
    fi
    
    # iptables 설정 (CentOS/RHEL)
    if command -v iptables &> /dev/null && ! command -v ufw &> /dev/null; then
        # 기본 정책 설정
        iptables -P INPUT DROP
        iptables -P FORWARD DROP
        iptables -P OUTPUT ACCEPT
        
        # 로컬 루프백 허용
        iptables -A INPUT -i lo -j ACCEPT
        
        # ESTABLISHED 연결 허용
        iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
        
        # 필요한 포트 허용
        iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
        iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
        iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
        iptables -A INPUT -p tcp --dport 8000 -j ACCEPT # API Gateway
        iptables -A INPUT -p tcp --dport 5001 -j ACCEPT # Backend
        iptables -A INPUT -p tcp --dport 8002 -j ACCEPT # AI Server
        iptables -A INPUT -p tcp --dport 3000 -j ACCEPT # Frontend
        iptables -A INPUT -p tcp --dport 5432 -j ACCEPT # PostgreSQL
        iptables -A INPUT -p tcp --dport 6379 -j ACCEPT # Redis
        
        # iptables 규칙 저장
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4
        fi
        
        log_success "iptables firewall configured"
    fi
    
    # SSH 보안 강화
    log_info "Hardening SSH configuration..."
    
    # sshd_config 백업
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # SSH 보안 설정
    cat > /tmp/sshd_secure.conf << EOF
# SSH 보안 설정
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# 인증 설정
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes

# 세션 설정
X11Forwarding no
AllowTcpForwarding no
GatewayPorts no
PermitTunnel no
MaxAuthTries 3
MaxSessions 10
ClientAliveInterval 300
ClientAliveCountMax 2

# 로깅
SyslogFacility AUTH
LogLevel INFO

# 접근 제한
AllowUsers your_program
DenyUsers root admin
EOF

    # SSH 설정 적용
    cp /tmp/sshd_secure.conf /etc/ssh/sshd_config
    systemctl restart sshd
    
    log_success "SSH security hardened"
    
    # 시스템 업데이트
    log_info "Updating system packages..."
    
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get upgrade -y
    elif command -v yum &> /dev/null; then
        yum update -y
    elif command -v dnf &> /dev/null; then
        dnf update -y
    fi
    
    log_success "System packages updated"
}

# 네트워크 보안 강화
harden_network() {
    log_info "Hardening network security..."
    
    # 네트워크 인터페이스 보안
    log_info "Securing network interfaces..."
    
    # IP 스푸핑 방지
    echo "net.ipv4.conf.all.rp_filter=1" >> /etc/sysctl.conf
    echo "net.ipv4.conf.default.rp_filter=1" >> /etc/sysctl.conf
    
    # ICMP 리다이렉트 비활성화
    echo "net.ipv4.conf.all.accept_redirects=0" >> /etc/sysctl.conf
    echo "net.ipv4.conf.default.accept_redirects=0" >> /etc/sysctl.conf
    
    # 소스 라우팅 비활성화
    echo "net.ipv4.conf.all.accept_source_route=0" >> /etc/sysctl.conf
    echo "net.ipv4.conf.default.accept_source_route=0" >> /etc/sysctl.conf
    
    # sysctl 설정 적용
    sysctl -p
    
    # DNS 보안
    log_info "Securing DNS configuration..."
    
    # DNS 오버 HTTPS 설정
    cat > /etc/systemd/resolved.conf << EOF
[Resolve]
DNS=1.1.1.1 1.0.0.1 8.8.8.8 8.8.4.4
DNSOverTLS=yes
DNSSEC=yes
EOF

    systemctl restart systemd-resolved
    
    log_success "Network security hardened"
}

# 애플리케이션 보안 강화
harden_application() {
    log_info "Hardening application security..."
    
    # Docker 보안 설정
    log_info "Securing Docker configuration..."
    
    # Docker 데몬 보안 설정
    cat > /etc/docker/daemon.json << EOF
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp-profile.json"
}
EOF

    # Docker 보안 프로필 생성
    mkdir -p /etc/docker
    cat > /etc/docker/seccomp-profile.json << EOF
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_AARCH64"
  ],
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "access",
        "arch_prctl",
        "bind",
        "brk",
        "capget",
        "capset",
        "chdir",
        "clock_gettime",
        "clone",
        "close",
        "connect",
        "dup",
        "dup2",
        "dup3",
        "epoll_create",
        "epoll_create1",
        "epoll_ctl",
        "epoll_ctl_old",
        "epoll_pwait",
        "epoll_wait",
        "epoll_wait_old",
        "execve",
        "exit",
        "exit_group",
        "faccessat",
        "fchdir",
        "fcntl",
        "fdatasync",
        "flock",
        "fork",
        "fstat",
        "fstatfs",
        "futex",
        "getcwd",
        "getdents",
        "getdents64",
        "getegid",
        "geteuid",
        "getgid",
        "getpeername",
        "getpid",
        "getppid",
        "getrandom",
        "getrlimit",
        "getsockname",
        "getsockopt",
        "gettid",
        "gettimeofday",
        "getuid",
        "ioctl",
        "listen",
        "lseek",
        "lstat",
        "madvise",
        "mkdir",
        "mmap",
        "mprotect",
        "mremap",
        "munmap",
        "nanosleep",
        "newfstatat",
        "open",
        "openat",
        "pipe",
        "pipe2",
        "poll",
        "pread64",
        "prlimit64",
        "pwrite64",
        "read",
        "readlink",
        "readlinkat",
        "recvfrom",
        "recvmsg",
        "rename",
        "renameat",
        "rt_sigaction",
        "rt_sigprocmask",
        "rt_sigreturn",
        "rt_sigsuspend",
        "rt_sigtimedwait",
        "sched_getaffinity",
        "sched_yield",
        "select",
        "sendfile",
        "sendmmsg",
        "sendmsg",
        "sendto",
        "set_robust_list",
        "set_tid_address",
        "setgid",
        "setgroups",
        "setuid",
        "shutdown",
        "socket",
        "socketpair",
        "stat",
        "statfs",
        "sysinfo",
        "tgkill",
        "time",
        "uname",
        "unlink",
        "unlinkat",
        "vfork",
        "wait4",
        "waitid",
        "waitpid",
        "write",
        "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

    # Docker 서비스 재시작
    systemctl restart docker
    
    # 애플리케이션 보안 헤더 설정
    log_info "Configuring security headers..."
    
    # Nginx 보안 헤더 강화
    cat > /tmp/nginx_security.conf << EOF
# 보안 헤더
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' ws: wss:;" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Rate Limiting 강화
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone \$binary_remote_addr zone=admin:10m rate=5r/s;

# 요청 크기 제한
client_max_body_size 10M;
client_body_buffer_size 128k;

# 타임아웃 설정
client_body_timeout 10s;
client_header_timeout 10s;
keepalive_timeout 65;
send_timeout 10s;
EOF

    # Nginx 설정 적용
    docker cp /tmp/nginx_security.conf nginx:/etc/nginx/conf.d/security.conf
    docker-compose exec nginx nginx -s reload
    
    log_success "Application security hardened"
}

# 데이터베이스 보안 강화
harden_database() {
    log_info "Hardening database security..."
    
    # PostgreSQL 보안 설정
    log_info "Securing PostgreSQL configuration..."
    
    # pg_hba.conf 보안 설정
    cat > /tmp/pg_hba_secure.conf << EOF
# PostgreSQL 클라이언트 인증 설정
local   all             postgres                                peer
local   all             your_program                            md5
host    all             your_program        127.0.0.1/32        md5
host    all             your_program        ::1/128             md5
host    your_program    your_program        127.0.0.1/32        md5
host    your_program_ai your_program_ai     127.0.0.1/32        md5
EOF

    # postgresql.conf 보안 설정
    cat > /tmp/postgresql_secure.conf << EOF
# 보안 설정
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on

# 연결 제한
max_connections = 100
superuser_reserved_connections = 3

# 로깅
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_statement = 'all'
log_min_duration_statement = 1000
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# 인증
password_encryption = scram-sha-256
EOF

    # 데이터베이스 보안 설정 적용
    docker cp /tmp/pg_hba_secure.conf postgres:/var/lib/postgresql/data/pg_hba.conf
    docker cp /tmp/postgresql_secure.conf postgres:/var/lib/postgresql/data/postgresql.conf
    docker-compose restart postgres
    
    # Redis 보안 설정
    log_info "Securing Redis configuration..."
    
    cat > /tmp/redis_secure.conf << EOF
# Redis 보안 설정
requirepass your_strong_redis_password_here
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command BGSAVE ""
rename-command SAVE ""

# 네트워크 보안
bind 127.0.0.1
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300

# 메모리 보안
maxmemory 512mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# 로깅
loglevel notice
logfile ""
syslog-enabled no
EOF

    # Redis 설정 적용
    docker cp /tmp/redis_secure.conf redis:/usr/local/etc/redis/redis.conf
    docker-compose restart redis
    
    log_success "Database security hardened"
}

# 보안 스캔
scan_security() {
    log_info "Scanning for security vulnerabilities..."
    
    echo "=== Security Scan Report ===" > "$SECURITY_LOG"
    echo "Timestamp: $(date)" >> "$SECURITY_LOG"
    echo "" >> "$SECURITY_LOG"
    
    # 포트 스캔
    log_info "Scanning open ports..."
    
    echo "=== Open Ports ===" >> "$SECURITY_LOG"
    netstat -tuln >> "$SECURITY_LOG" 2>&1
    
    # 취약한 서비스 확인
    log_info "Checking vulnerable services..."
    
    echo "" >> "$SECURITY_LOG"
    echo "=== Service Security Check ===" >> "$SECURITY_LOG"
    
    # SSH 설정 확인
    echo "SSH Configuration:" >> "$SECURITY_LOG"
    grep -E "^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config >> "$SECURITY_LOG" 2>&1 || echo "SSH config not found" >> "$SECURITY_LOG"
    
    # 방화벽 상태 확인
    echo "" >> "$SECURITY_LOG"
    echo "Firewall Status:" >> "$SECURITY_LOG"
    if command -v ufw &> /dev/null; then
        ufw status >> "$SECURITY_LOG" 2>&1
    elif command -v iptables &> /dev/null; then
        iptables -L >> "$SECURITY_LOG" 2>&1
    fi
    
    # Docker 보안 스캔
    log_info "Scanning Docker containers..."
    
    echo "" >> "$SECURITY_LOG"
    echo "=== Docker Security Scan ===" >> "$SECURITY_LOG"
    
    # 실행 중인 컨테이너 확인
    echo "Running Containers:" >> "$SECURITY_LOG"
    docker ps >> "$SECURITY_LOG" 2>&1
    
    # 컨테이너 취약점 스캔
    if command -v trivy &> /dev/null; then
        echo "" >> "$SECURITY_LOG"
        echo "Container Vulnerability Scan:" >> "$SECURITY_LOG"
        for container in $(docker ps --format "{{.Names}}"); do
            echo "Scanning $container:" >> "$SECURITY_LOG"
            trivy image $(docker inspect $container --format='{{.Image}}') >> "$SECURITY_LOG" 2>&1
        done
    fi
    
    # 애플리케이션 보안 헤더 확인
    log_info "Checking security headers..."
    
    echo "" >> "$SECURITY_LOG"
    echo "=== Security Headers Check ===" >> "$SECURITY_LOG"
    
    # 주요 엔드포인트 보안 헤더 확인
    for url in "http://localhost" "http://localhost:8000" "http://localhost:5001"; do
        echo "Checking $url:" >> "$SECURITY_LOG"
        curl -I "$url" 2>/dev/null | grep -E "(X-Frame-Options|X-XSS-Protection|X-Content-Type-Options|Strict-Transport-Security)" >> "$SECURITY_LOG" 2>&1 || echo "No security headers found" >> "$SECURITY_LOG"
    done
    
    log_success "Security scan completed. Results saved to $SECURITY_LOG"
}

# 보안 감사
audit_security() {
    log_info "Performing security audit..."
    
    echo "=== Security Audit Report ===" > "$SECURITY_LOG"
    echo "Timestamp: $(date)" >> "$SECURITY_LOG"
    echo "" >> "$SECURITY_LOG"
    
    # 시스템 보안 감사
    log_info "Auditing system security..."
    
    echo "=== System Security Audit ===" >> "$SECURITY_LOG"
    
    # 사용자 계정 감사
    echo "User Accounts:" >> "$SECURITY_LOG"
    cat /etc/passwd | grep -E ":[0-9]{4}:" >> "$SECURITY_LOG"
    
    # 그룹 권한 감사
    echo "" >> "$SECURITY_LOG"
    echo "Group Permissions:" >> "$SECURITY_LOG"
    cat /etc/group >> "$SECURITY_LOG"
    
    # 파일 권한 감사
    echo "" >> "$SECURITY_LOG"
    echo "Critical File Permissions:" >> "$SECURITY_LOG"
    ls -la /etc/passwd /etc/shadow /etc/group /etc/gshadow >> "$SECURITY_LOG" 2>&1
    
    # 네트워크 연결 감사
    log_info "Auditing network connections..."
    
    echo "" >> "$SECURITY_LOG"
    echo "=== Network Audit ===" >> "$SECURITY_LOG"
    
    echo "Active Connections:" >> "$SECURITY_LOG"
    netstat -tuln >> "$SECURITY_LOG" 2>&1
    
    echo "" >> "$SECURITY_LOG"
    echo "Listening Services:" >> "$SECURITY_LOG"
    ss -tuln >> "$SECURITY_LOG" 2>&1
    
    # 로그 감사
    log_info "Auditing system logs..."
    
    echo "" >> "$SECURITY_LOG"
    echo "=== Log Audit ===" >> "$SECURITY_LOG"
    
    # 인증 실패 로그
    echo "Authentication Failures:" >> "$SECURITY_LOG"
    grep "Failed password" /var/log/auth.log 2>/dev/null | tail -10 >> "$SECURITY_LOG" || echo "No auth.log found" >> "$SECURITY_LOG"
    
    # SSH 로그인 시도
    echo "" >> "$SECURITY_LOG"
    echo "SSH Login Attempts:" >> "$SECURITY_LOG"
    grep "sshd" /var/log/auth.log 2>/dev/null | tail -10 >> "$SECURITY_LOG" || echo "No SSH logs found" >> "$SECURITY_LOG"
    
    log_success "Security audit completed. Results saved to $SECURITY_LOG"
}

# 메인 로직
main() {
    log_info "Your Program Security Hardening"
    log_info "Target: $TARGET"
    log_info "Action: $ACTION"
    
    # 로그 디렉토리 생성
    mkdir -p "$PROJECT_ROOT/logs"
    
    case $ACTION in
        "harden")
            case $TARGET in
                "system")
                    harden_system
                    ;;
                "network")
                    harden_network
                    ;;
                "application")
                    harden_application
                    ;;
                "database")
                    harden_database
                    ;;
                "all")
                    harden_system
                    harden_network
                    harden_application
                    harden_database
                    ;;
                *)
                    log_error "Invalid target: $TARGET"
                    exit 1
                    ;;
            esac
            ;;
            
        "scan")
            scan_security
            ;;
            
        "audit")
            audit_security
            ;;
            
        *)
            log_error "Invalid action: $ACTION"
            exit 1
            ;;
    esac
    
    log_success "Security hardening process completed"
}

# 스크립트 실행
main "$@" 