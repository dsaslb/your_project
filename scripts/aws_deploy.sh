#!/bin/bash

# AWS 클라우드 배포 스크립트
# Your Program 엔터프라이즈급 시스템 배포

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
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

# 환경 변수 설정
export AWS_REGION=${AWS_REGION:-"us-east-1"}
export PROJECT_NAME="your-program"
export ENVIRONMENT=${ENVIRONMENT:-"production"}
export DOMAIN_NAME=${DOMAIN_NAME:-"yourdomain.com"}
export SSL_EMAIL=${SSL_EMAIL:-"admin@yourdomain.com"}

# 스택 이름
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}"

# 배포 시작
log_info "🚀 Your Program AWS 배포 시작"
log_info "지역: $AWS_REGION"
log_info "환경: $ENVIRONMENT"
log_info "도메인: $DOMAIN_NAME"

# 1. AWS CLI 및 도구 확인
check_prerequisites() {
    log_info "📋 사전 요구사항 확인 중..."
    
    # AWS CLI 확인
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI가 설치되지 않았습니다."
        exit 1
    fi
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    # kubectl 확인
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl이 설치되지 않았습니다."
        exit 1
    fi
    
    # AWS 자격 증명 확인
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS 자격 증명이 설정되지 않았습니다."
        exit 1
    fi
    
    log_success "사전 요구사항 확인 완료"
}

# 2. ECR 리포지토리 생성
create_ecr_repositories() {
    log_info "🐳 ECR 리포지토리 생성 중..."
    
    # 백엔드 리포지토리
    aws ecr create-repository \
        --repository-name "${PROJECT_NAME}/backend" \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256 || true
    
    # 프론트엔드 리포지토리
    aws ecr create-repository \
        --repository-name "${PROJECT_NAME}/frontend" \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256 || true
    
    log_success "ECR 리포지토리 생성 완료"
}

# 3. Docker 이미지 빌드 및 푸시
build_and_push_images() {
    log_info "🔨 Docker 이미지 빌드 및 푸시 중..."
    
    # ECR 로그인
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
    
    # 백엔드 이미지 빌드
    log_info "백엔드 이미지 빌드 중..."
    docker build -t ${PROJECT_NAME}/backend:latest -f Dockerfile.production .
    
    # 백엔드 이미지 태그 및 푸시
    BACKEND_ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/${PROJECT_NAME}/backend
    docker tag ${PROJECT_NAME}/backend:latest $BACKEND_ECR_URI:latest
    docker push $BACKEND_ECR_URI:latest
    
    # 프론트엔드 이미지 빌드
    log_info "프론트엔드 이미지 빌드 중..."
    docker build -t ${PROJECT_NAME}/frontend:latest -f frontend/Dockerfile.production ./frontend
    
    # 프론트엔드 이미지 태그 및 푸시
    FRONTEND_ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/${PROJECT_NAME}/frontend
    docker tag ${PROJECT_NAME}/frontend:latest $FRONTEND_ECR_URI:latest
    docker push $FRONTEND_ECR_URI:latest
    
    log_success "Docker 이미지 빌드 및 푸시 완료"
}

# 4. EKS 클러스터 생성
create_eks_cluster() {
    log_info "☸️ EKS 클러스터 생성 중..."
    
    # eksctl을 사용한 클러스터 생성
    eksctl create cluster \
        --name ${PROJECT_NAME}-cluster \
        --region $AWS_REGION \
        --nodegroup-name ${PROJECT_NAME}-nodes \
        --node-type t3.medium \
        --nodes 3 \
        --nodes-min 2 \
        --nodes-max 5 \
        --managed \
        --with-oidc \
        --ssh-access \
        --ssh-public-key my-key \
        --full-ecr-access \
        --appmesh-access \
        --alb-ingress-access || true
    
    log_success "EKS 클러스터 생성 완료"
}

# 5. Kubernetes 리소스 배포
deploy_kubernetes_resources() {
    log_info "📦 Kubernetes 리소스 배포 중..."
    
    # 네임스페이스 생성
    kubectl apply -f k8s/namespace.yaml
    
    # ConfigMap 및 Secret 생성
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secret.yaml
    
    # 데이터베이스 배포
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/redis.yaml
    
    # 애플리케이션 배포
    kubectl apply -f k8s/backend.yaml
    kubectl apply -f k8s/frontend.yaml
    
    # 모니터링 배포
    kubectl apply -f k8s/monitoring.yaml
    
    # 인그레스 배포
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Kubernetes 리소스 배포 완료"
}

# 6. SSL 인증서 설정
setup_ssl_certificate() {
    log_info "🔒 SSL 인증서 설정 중..."
    
    # cert-manager 설치
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
    
    # ClusterIssuer 생성
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: $SSL_EMAIL
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
    
    log_success "SSL 인증서 설정 완료"
}

# 7. 모니터링 설정
setup_monitoring() {
    log_info "📊 모니터링 설정 중..."
    
    # Prometheus Operator 설치
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.enabled=true \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
    
    # Grafana 대시보드 설정
    kubectl apply -f k8s/grafana-dashboards.yaml
    
    log_success "모니터링 설정 완료"
}

# 8. 백업 설정
setup_backup() {
    log_info "💾 백업 설정 중..."
    
    # Velero 설치 (백업 솔루션)
    helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
    helm repo update
    
    helm install velero vmware-tanzu/velero \
        --namespace velero \
        --create-namespace \
        --set configuration.provider=aws \
        --set configuration.backupStorageLocation.name=default \
        --set configuration.backupStorageLocation.bucket=your-program-backups \
        --set configuration.volumeSnapshotLocation.name=default \
        --set configuration.volumeSnapshotLocation.config.region=$AWS_REGION \
        --set credentials.useSecret=false \
        --set initContainers[0].name=velero-plugin-for-aws \
        --set initContainers[0].image=velero/velero-plugin-for-aws:v1.7.0 \
        --set initContainers[0].volumeMounts[0].mountPath=/target \
        --set initContainers[0].volumeMounts[0].name=plugins
    
    log_success "백업 설정 완료"
}

# 9. CI/CD 파이프라인 설정
setup_cicd() {
    log_info "🔄 CI/CD 파이프라인 설정 중..."
    
    # GitHub Actions 워크플로우 파일 생성
    cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to AWS

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  AWS_REGION: us-east-1
  EKS_CLUSTER_NAME: your-program-cluster

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: |
        pip install -r requirements.txt
        python -m pytest tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Update kube config
      run: aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER_NAME }} --region ${{ env.AWS_REGION }}
    
    - name: Deploy to EKS
      run: |
        kubectl apply -f k8s/
        kubectl rollout restart deployment/backend -n your-program
        kubectl rollout restart deployment/frontend -n your-program
EOF
    
    log_success "CI/CD 파이프라인 설정 완료"
}

# 10. 배포 검증
verify_deployment() {
    log_info "✅ 배포 검증 중..."
    
    # 파드 상태 확인
    kubectl get pods -n your-program
    
    # 서비스 상태 확인
    kubectl get services -n your-program
    
    # 인그레스 상태 확인
    kubectl get ingress -n your-program
    
    # 애플리케이션 헬스체크
    sleep 30
    curl -f https://$DOMAIN_NAME/health || log_warning "애플리케이션 헬스체크 실패"
    
    log_success "배포 검증 완료"
}

# 11. 배포 완료 정보 출력
show_deployment_info() {
    log_success "🎉 배포 완료!"
    
    echo ""
    echo "📋 배포 정보:"
    echo "  - 애플리케이션 URL: https://$DOMAIN_NAME"
    echo "  - API URL: https://api.$DOMAIN_NAME"
    echo "  - Grafana 대시보드: https://grafana.$DOMAIN_NAME"
    echo "  - Kibana 로그: https://kibana.$DOMAIN_NAME"
    echo ""
    echo "🔧 관리 명령어:"
    echo "  - 클러스터 상태 확인: kubectl get nodes"
    echo "  - 파드 상태 확인: kubectl get pods -n your-program"
    echo "  - 로그 확인: kubectl logs -f deployment/backend -n your-program"
    echo "  - 스케일링: kubectl scale deployment backend --replicas=5 -n your-program"
    echo ""
    echo "📊 모니터링:"
    echo "  - Prometheus: kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
    echo "  - Grafana: kubectl port-forward svc/grafana 3000:3000 -n monitoring"
    echo ""
}

# 메인 실행 함수
main() {
    log_info "🚀 Your Program AWS 클라우드 배포 시작"
    
    check_prerequisites
    create_ecr_repositories
    build_and_push_images
    create_eks_cluster
    deploy_kubernetes_resources
    setup_ssl_certificate
    setup_monitoring
    setup_backup
    setup_cicd
    verify_deployment
    show_deployment_info
    
    log_success "🎉 AWS 클라우드 배포 완료!"
}

# 스크립트 실행
main "$@" 