# 🚀 Kubernetes 배포 및 모니터링 가이드

## 📋 개요

레스토랑 관리 시스템을 Kubernetes 클러스터에 배포하고 Prometheus + Grafana를 통한 고급 모니터링을 설정합니다.

## 🏗️ 아키텍처 구조

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │  restaurant-    │  │    monitoring   │              │
│  │    system       │  │   namespace     │              │
│  │  namespace      │  │                 │              │
│  │                 │  │                 │              │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │              │
│  │ │ API Gateway │ │  │ │ Prometheus  │ │              │
│  │ │ (3 replicas)│ │  │ │             │ │              │
│  │ └─────────────┘ │  │ └─────────────┘ │              │
│  │                 │  │                 │              │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │              │
│  │ │ User Service│ │  │ │   Grafana   │ │              │
│  │ │ (2 replicas)│ │  │ │             │ │              │
│  │ └─────────────┘ │  │ └─────────────┘ │              │
│  │                 │  │                 │              │
│  │ ┌─────────────┐ │  └─────────────────┘              │
│  │ │ IoT Service │ │                                   │
│  │ │ (2 replicas)│ │                                   │
│  │ └─────────────┘ │                                   │
│  │                 │                                   │
│  │ ┌─────────────┐ │                                   │
│  │ │ PostgreSQL  │ │                                   │
│  │ └─────────────┘ │                                   │
│  │                 │                                   │
│  │ ┌─────────────┐ │                                   │
│  │ │    Redis    │ │                                   │
│  │ └─────────────┘ │                                   │
│  └─────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

## 🚀 배포 방법

### 1. 직접 Kubernetes 배포

```bash
# 네임스페이스 생성
kubectl apply -f namespaces/restaurant-system.yaml

# ConfigMap 및 Secret 생성
kubectl apply -f configmaps/app-config.yaml
kubectl apply -f secrets/app-secrets.yaml

# 애플리케이션 배포
kubectl apply -f deployments/
kubectl apply -f services/
kubectl apply -f ingress/

# 모니터링 배포
kubectl apply -f monitoring/
```

### 2. Helm을 사용한 배포

```bash
# Helm 저장소 추가
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 의존성 업데이트
helm dependency update

# 배포
helm install restaurant-management . --namespace restaurant-system --create-namespace
```

### 3. 배치 파일 사용

```bash
# Windows 배치 파일
deploy-kubernetes.bat

# 또는 Helm 배치 파일
deploy-helm.bat
```

## 📊 모니터링 시스템

### Prometheus 설정

- **데이터 수집**: 15초 간격으로 메트릭 수집
- **저장 기간**: 200시간 (약 8일)
- **대상 서비스**:
  - API Gateway
  - User Service
  - IoT Service
  - PostgreSQL
  - Redis
  - Kubernetes 노드 및 서비스

### Grafana 설정

- **기본 로그인**: admin / admin123
- **데이터소스**: Prometheus 자동 연결
- **대시보드**: 레스토랑 관리 시스템 전용 대시보드

### 메트릭 수집

#### 애플리케이션 메트릭
- HTTP 요청 수 및 응답 시간
- 에러율 및 성공률
- 메모리 및 CPU 사용량
- 데이터베이스 연결 상태

#### 인프라 메트릭
- Kubernetes 노드 상태
- Pod 상태 및 재시작 횟수
- 네트워크 트래픽
- 디스크 사용량

## 🔧 설정 파일

### 네임스페이스
- `namespaces/restaurant-system.yaml`: 애플리케이션 네임스페이스
- `namespaces/monitoring.yaml`: 모니터링 네임스페이스

### 설정 관리
- `configmaps/app-config.yaml`: 애플리케이션 설정
- `secrets/app-secrets.yaml`: 보안 정보

### 배포
- `deployments/gateway-deployment.yaml`: API Gateway
- `deployments/user-deployment.yaml`: User Service
- `deployments/iot-deployment.yaml`: IoT Service

### 서비스
- `services/app-services.yaml`: 모든 서비스 정의

### 인그레스
- `ingress/app-ingress.yaml`: 라우팅 규칙

### 모니터링
- `monitoring/prometheus-config.yaml`: Prometheus 설정
- `monitoring/prometheus-deployment.yaml`: Prometheus 배포
- `monitoring/grafana-deployment.yaml`: Grafana 배포
- `monitoring/grafana-datasources.yaml`: Grafana 데이터소스

## 🌐 접근 URL

### 애플리케이션
- **API Gateway**: http://api.restaurant.local
- **Admin Dashboard**: http://admin.restaurant.local
- **IoT Dashboard**: http://iot.restaurant.local

### 모니터링
- **Grafana**: http://grafana.restaurant.local
- **Prometheus**: http://prometheus.restaurant.local

## 📈 자동 스케일링

### Horizontal Pod Autoscaler (HPA)
- **API Gateway**: 2-10 replicas (CPU 70%, Memory 80%)
- **User Service**: 2-5 replicas (CPU 70%, Memory 80%)
- **IoT Service**: 2-5 replicas (CPU 70%, Memory 80%)

### 리소스 제한
- **API Gateway**: 128Mi-256Mi RAM, 100m-200m CPU
- **User Service**: 256Mi-512Mi RAM, 150m-300m CPU
- **IoT Service**: 512Mi-1Gi RAM, 200m-500m CPU

## 🔍 모니터링 및 로깅

### 상태 확인
```bash
# Pod 상태 확인
kubectl get pods -n restaurant-system
kubectl get pods -n monitoring

# 서비스 상태 확인
kubectl get services -n restaurant-system
kubectl get services -n monitoring

# Ingress 상태 확인
kubectl get ingress -n restaurant-system
kubectl get ingress -n monitoring
```

### 로그 확인
```bash
# API Gateway 로그
kubectl logs -f deployment/gateway-deployment -n restaurant-system

# User Service 로그
kubectl logs -f deployment/user-deployment -n restaurant-system

# IoT Service 로그
kubectl logs -f deployment/iot-deployment -n restaurant-system
```

### 메트릭 확인
```bash
# Prometheus 메트릭
kubectl port-forward svc/prometheus-service 9090:9090 -n monitoring

# Grafana 대시보드
kubectl port-forward svc/grafana-service 3000:3000 -n monitoring
```

## 🔒 보안 설정

### TLS/SSL
- Let's Encrypt 인증서 자동 발급
- HTTPS 강제 리다이렉트
- mTLS 지원 (향후 구현)

### 접근 제어
- 네임스페이스별 리소스 격리
- RBAC (Role-Based Access Control)
- Network Policies

### Rate Limiting
- Ingress 레벨에서 100 req/min 제한
- 서비스별 개별 제한 설정 가능

## 🚀 성능 최적화

### 리소스 관리
- **요청/제한 설정**: 안정적인 리소스 할당
- **Pod Disruption Budget**: 무중단 배포 보장
- **Anti-Affinity**: Pod 분산 배치

### 네트워크 최적화
- **Service Mesh**: Istio 통합 (향후 구현)
- **Load Balancing**: Kubernetes 기본 로드밸런서
- **Ingress Controller**: NGINX Ingress Controller

### 스토리지 최적화
- **Persistent Volumes**: 데이터 영속성 보장
- **Storage Classes**: 동적 프로비저닝
- **Backup Strategy**: 정기 백업 (향후 구현)

## 🔄 CI/CD 파이프라인

### 배포 전략
- **Blue-Green Deployment**: 무중단 배포
- **Rolling Update**: 점진적 업데이트
- **Canary Deployment**: A/B 테스트 (향후 구현)

### 자동화
- **GitOps**: ArgoCD 통합 (향후 구현)
- **Image Scanning**: 보안 취약점 검사
- **Automated Testing**: 배포 전 자동 테스트

## 📝 트러블슈팅

### 일반적인 문제

#### 1. Pod가 시작되지 않는 경우
```bash
# Pod 상태 확인
kubectl describe pod <pod-name> -n restaurant-system

# 로그 확인
kubectl logs <pod-name> -n restaurant-system
```

#### 2. 서비스 연결 문제
```bash
# 서비스 엔드포인트 확인
kubectl get endpoints -n restaurant-system

# 네트워크 정책 확인
kubectl get networkpolicies -n restaurant-system
```

#### 3. 모니터링 데이터가 수집되지 않는 경우
```bash
# Prometheus 타겟 상태 확인
kubectl port-forward svc/prometheus-service 9090:9090 -n monitoring
# 브라우저에서 http://localhost:9090/targets 접속
```

### 유용한 명령어
```bash
# 모든 리소스 확인
kubectl get all -n restaurant-system

# 이벤트 확인
kubectl get events -n restaurant-system

# 리소스 사용량 확인
kubectl top pods -n restaurant-system
kubectl top nodes

# 설정 확인
kubectl describe configmap restaurant-app-config -n restaurant-system
```

## 🎯 다음 단계

### Phase 10-3: 고급 모니터링
- **Jaeger**: 분산 추적 시스템
- **ELK Stack**: 로그 집계 및 분석
- **AlertManager**: 알림 시스템

### Phase 10-4: 보안 강화
- **mTLS**: 서비스 간 암호화 통신
- **OPA**: 정책 기반 접근 제어
- **Falco**: 런타임 보안 모니터링

### Phase 10-5: 성능 최적화
- **Istio**: 서비스 메시
- **KEDA**: 이벤트 기반 자동 스케일링
- **ArgoCD**: GitOps 배포

---

## 📞 지원

Kubernetes 배포 및 모니터링 관련 문제가 발생하면 개발팀에 문의해주세요. 