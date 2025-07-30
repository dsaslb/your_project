#!/bin/bash

# Azure 클라우드 배포 스크립트
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
export AZURE_LOCATION=${AZURE_LOCATION:-"eastus"}
export PROJECT_NAME="your-program"
export ENVIRONMENT=${ENVIRONMENT:-"production"}
export DOMAIN_NAME=${DOMAIN_NAME:-"yourdomain.com"}
export SSL_EMAIL=${SSL_EMAIL:-"admin@yourdomain.com"}

# 리소스 그룹 및 스택 이름
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"
AKS_CLUSTER_NAME="${PROJECT_NAME}-${ENVIRONMENT}-aks"
ACR_NAME="${PROJECT_NAME}acr${RANDOM}"

# 배포 시작
log_info "🚀 Your Program Azure 배포 시작"
log_info "지역: $AZURE_LOCATION"
log_info "환경: $ENVIRONMENT"
log_info "도메인: $DOMAIN_NAME"

# 1. Azure CLI 확인
check_prerequisites() {
    log_info "📋 사전 요구사항 확인 중..."
    
    # Azure CLI 확인
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI가 설치되지 않았습니다."
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
    
    # Azure 로그인 확인
    if ! az account show &> /dev/null; then
        log_error "Azure에 로그인되지 않았습니다. 'az login'을 실행하세요."
        exit 1
    fi
    
    log_success "사전 요구사항 확인 완료"
}

# 2. 리소스 그룹 생성
create_resource_group() {
    log_info "📦 리소스 그룹 생성 중..."
    
    az group create \
        --name $RESOURCE_GROUP \
        --location $AZURE_LOCATION \
        --tags Environment=$ENVIRONMENT Project=$PROJECT_NAME
    
    log_success "리소스 그룹 생성 완료: $RESOURCE_GROUP"
}

# 3. Azure Container Registry 생성
create_acr() {
    log_info "🐳 Azure Container Registry 생성 중..."
    
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Premium \
        --admin-enabled true
    
    # ACR 로그인
    az acr login --name $ACR_NAME
    
    log_success "ACR 생성 완료: $ACR_NAME"
}

# 4. AKS 클러스터 생성
create_aks_cluster() {
    log_info "☸️ AKS 클러스터 생성 중..."
    
    az aks create \
        --resource-group $RESOURCE_GROUP \
        --name $AKS_CLUSTER_NAME \
        --node-count 3 \
        --node-vm-size Standard_D2s_v3 \
        --enable-addons monitoring \
        --generate-ssh-keys \
        --attach-acr $ACR_NAME \
        --network-plugin azure \
        --network-policy azure \
        --enable-managed-identity
    
    # kubectl 자격 증명 가져오기
    az aks get-credentials \
        --resource-group $RESOURCE_GROUP \
        --name $AKS_CLUSTER_NAME \
        --overwrite-existing
    
    log_success "AKS 클러스터 생성 완료: $AKS_CLUSTER_NAME"
}

# 5. Docker 이미지 빌드 및 푸시
build_and_push_images() {
    log_info "🔨 Docker 이미지 빌드 및 푸시 중..."
    
    # ACR 로그인
    az acr login --name $ACR_NAME
    
    # 백엔드 이미지 빌드
    log_info "백엔드 이미지 빌드 중..."
    docker build -t ${ACR_NAME}.azurecr.io/${PROJECT_NAME}/backend:latest -f Dockerfile.production .
    docker push ${ACR_NAME}.azurecr.io/${PROJECT_NAME}/backend:latest
    
    # 프론트엔드 이미지 빌드
    log_info "프론트엔드 이미지 빌드 중..."
    docker build -t ${ACR_NAME}.azurecr.io/${PROJECT_NAME}/frontend:latest -f frontend/Dockerfile.production ./frontend
    docker push ${ACR_NAME}.azurecr.io/${PROJECT_NAME}/frontend:latest
    
    log_success "Docker 이미지 빌드 및 푸시 완료"
}

# 6. Azure Database for PostgreSQL 생성
create_postgresql() {
    log_info "🐘 Azure Database for PostgreSQL 생성 중..."
    
    az postgres flexible-server create \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-postgres" \
        --location $AZURE_LOCATION \
        --admin-user postgres \
        --admin-password "YourSecurePassword123!" \
        --sku-name Standard_B1ms \
        --version 15 \
        --storage-size 32 \
        --storage-auto-grow Enabled \
        --backup-retention 7 \
        --geo-redundant-backup Disabled \
        --zone 1
    
    # 데이터베이스 생성
    az postgres flexible-server db create \
        --resource-group $RESOURCE_GROUP \
        --server-name "${PROJECT_NAME}-postgres" \
        --database-name your_program
    
    log_success "PostgreSQL 데이터베이스 생성 완료"
}

# 7. Azure Cache for Redis 생성
create_redis_cache() {
    log_info "🔴 Azure Cache for Redis 생성 중..."
    
    az redis create \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-redis" \
        --location $AZURE_LOCATION \
        --sku Basic \
        --vm-size c0 \
        --enable-non-ssl-port
    
    log_success "Redis 캐시 생성 완료"
}

# 8. Application Gateway 생성
create_application_gateway() {
    log_info "🌐 Application Gateway 생성 중..."
    
    # 가상 네트워크 생성
    az network vnet create \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-vnet" \
        --address-prefix 10.0.0.0/16 \
        --subnet-name default \
        --subnet-prefix 10.0.1.0/24
    
    # Application Gateway 서브넷 생성
    az network vnet subnet create \
        --resource-group $RESOURCE_GROUP \
        --vnet-name "${PROJECT_NAME}-vnet" \
        --name appgwsubnet \
        --address-prefix 10.0.2.0/24
    
    # 공용 IP 생성
    az network public-ip create \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-pip" \
        --allocation-method Static \
        --sku Standard
    
    # Application Gateway 생성
    az network application-gateway create \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-appgw" \
        --location $AZURE_LOCATION \
        --vnet-name "${PROJECT_NAME}-vnet" \
        --subnet appgwsubnet \
        --public-ip-address "${PROJECT_NAME}-pip" \
        --http-settings-cookie-based-affinity Enabled \
        --frontend-port 80 \
        --http-settings-port 80 \
        --http-settings-protocol Http \
        --routing-rule-type Basic \
        --sku Standard_v2 \
        --capacity 2
    
    log_success "Application Gateway 생성 완료"
}

# 9. Kubernetes 리소스 배포
deploy_kubernetes_resources() {
    log_info "📦 Kubernetes 리소스 배포 중..."
    
    # 네임스페이스 생성
    kubectl apply -f k8s/namespace.yaml
    
    # ConfigMap 및 Secret 생성 (Azure 리소스 정보로 업데이트)
    cat > k8s/configmap-azure.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: your-program-config
  namespace: your-program
data:
  FLASK_ENV: "production"
  DATABASE_URL: "postgresql://postgres:YourSecurePassword123!@${PROJECT_NAME}-postgres.postgres.database.azure.com:5432/your_program"
  REDIS_URL: "redis://${PROJECT_NAME}-redis.redis.cache.windows.net:6380"
  API_BASE_URL: "https://$DOMAIN_NAME"
  NEXT_PUBLIC_API_URL: "https://$DOMAIN_NAME"
EOF
    
    kubectl apply -f k8s/configmap-azure.yaml
    kubectl apply -f k8s/secret.yaml
    
    # 애플리케이션 배포
    kubectl apply -f k8s/backend-azure.yaml
    kubectl apply -f k8s/frontend-azure.yaml
    
    # 모니터링 배포
    kubectl apply -f k8s/monitoring-azure.yaml
    
    log_success "Kubernetes 리소스 배포 완료"
}

# 10. Azure Monitor 설정
setup_azure_monitor() {
    log_info "📊 Azure Monitor 설정 중..."
    
    # Log Analytics 작업 영역 생성
    az monitor log-analytics workspace create \
        --resource-group $RESOURCE_GROUP \
        --workspace-name "${PROJECT_NAME}-workspace"
    
    # Application Insights 생성
    az monitor app-insights component create \
        --app "${PROJECT_NAME}-appinsights" \
        --location $AZURE_LOCATION \
        --resource-group $RESOURCE_GROUP \
        --application-type web
    
    log_success "Azure Monitor 설정 완료"
}

# 11. Azure DevOps 파이프라인 설정
setup_azure_devops() {
    log_info "🔄 Azure DevOps 파이프라인 설정 중..."
    
    # Azure DevOps 프로젝트 생성 (CLI로는 제한적이므로 수동 설정 안내)
    log_info "Azure DevOps 프로젝트를 수동으로 생성하고 다음 YAML을 사용하세요:"
    
    cat > azure-pipelines.yml << 'EOF'
trigger:
- main

variables:
  dockerfilePath: '**/Dockerfile*'
  tag: '$(Build.BuildId)'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: Build
    displayName: 'Build'
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: Docker@2
      displayName: 'Build Backend Image'
      inputs:
        containerRegistry: 'your-acr-connection'
        repository: 'your-program/backend'
        command: 'buildAndPush'
        Dockerfile: '**/Dockerfile.production'
        tags: |
          $(tag)
          latest
    
    - task: Docker@2
      displayName: 'Build Frontend Image'
      inputs:
        containerRegistry: 'your-acr-connection'
        repository: 'your-program/frontend'
        command: 'buildAndPush'
        Dockerfile: 'frontend/Dockerfile.production'
        tags: |
          $(tag)
          latest

- stage: Deploy
  displayName: 'Deploy to AKS'
  dependsOn: Build
  jobs:
  - deployment: Deploy
    displayName: 'Deploy'
    pool:
      vmImage: 'ubuntu-latest'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: KubernetesManifest@0
            displayName: 'Deploy to AKS'
            inputs:
              action: 'deploy'
              kubernetesServiceConnection: 'your-aks-connection'
              manifests: 'k8s/*.yaml'
              containers: '$(ACR_NAME).azurecr.io/your-program/backend:$(tag)'
EOF
    
    log_success "Azure DevOps 파이프라인 설정 완료"
}

# 12. SSL 인증서 설정
setup_ssl_certificate() {
    log_info "🔒 SSL 인증서 설정 중..."
    
    # Azure Key Vault 생성
    az keyvault create \
        --name "${PROJECT_NAME}-kv" \
        --resource-group $RESOURCE_GROUP \
        --location $AZURE_LOCATION \
        --enabled-for-disk-encryption \
        --enabled-for-deployment \
        --enabled-for-template-deployment
    
    # cert-manager 설치
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
    
    # ClusterIssuer 생성 (Let's Encrypt)
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
          class: azure/application-gateway
EOF
    
    log_success "SSL 인증서 설정 완료"
}

# 13. 배포 검증
verify_deployment() {
    log_info "✅ 배포 검증 중..."
    
    # 파드 상태 확인
    kubectl get pods -n your-program
    
    # 서비스 상태 확인
    kubectl get services -n your-program
    
    # Application Gateway 상태 확인
    az network application-gateway show \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-appgw" \
        --query "provisioningState"
    
    log_success "배포 검증 완료"
}

# 14. 배포 완료 정보 출력
show_deployment_info() {
    log_success "🎉 Azure 배포 완료!"
    
    # 공용 IP 주소 가져오기
    PUBLIC_IP=$(az network public-ip show \
        --resource-group $RESOURCE_GROUP \
        --name "${PROJECT_NAME}-pip" \
        --query "ipAddress" \
        --output tsv)
    
    echo ""
    echo "📋 배포 정보:"
    echo "  - 리소스 그룹: $RESOURCE_GROUP"
    echo "  - AKS 클러스터: $AKS_CLUSTER_NAME"
    echo "  - ACR: $ACR_NAME"
    echo "  - 공용 IP: $PUBLIC_IP"
    echo "  - 애플리케이션 URL: https://$DOMAIN_NAME"
    echo ""
    echo "🔧 관리 명령어:"
    echo "  - 클러스터 연결: az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME"
    echo "  - 파드 상태 확인: kubectl get pods -n your-program"
    echo "  - 로그 확인: kubectl logs -f deployment/backend -n your-program"
    echo "  - 스케일링: kubectl scale deployment backend --replicas=5 -n your-program"
    echo ""
    echo "📊 모니터링:"
    echo "  - Azure Portal: https://portal.azure.com"
    echo "  - Application Insights: Azure Portal에서 확인"
    echo "  - Log Analytics: Azure Portal에서 확인"
    echo ""
}

# 메인 실행 함수
main() {
    log_info "🚀 Your Program Azure 클라우드 배포 시작"
    
    check_prerequisites
    create_resource_group
    create_acr
    create_aks_cluster
    build_and_push_images
    create_postgresql
    create_redis_cache
    create_application_gateway
    deploy_kubernetes_resources
    setup_azure_monitor
    setup_azure_devops
    setup_ssl_certificate
    verify_deployment
    show_deployment_info
    
    log_success "🎉 Azure 클라우드 배포 완료!"
}

# 스크립트 실행
main "$@" 