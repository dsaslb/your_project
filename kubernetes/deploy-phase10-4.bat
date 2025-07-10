@echo off
echo ========================================
echo Phase 10-4: 보안 강화 및 성능 최적화 배포
echo ========================================

echo.
echo 1. mTLS 인증서 생성...
if not exist "security\certs" (
    echo OpenSSL이 필요합니다. 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

echo.
echo 2. mTLS Secret 생성...
kubectl apply -f security/mtls-secrets.yaml

echo.
echo 3. OPA 정책 기반 접근 제어 배포...
kubectl apply -f security/opa-deployment.yaml
kubectl apply -f security/opa-policies.yaml

echo.
echo 4. Falco 런타임 보안 모니터링 배포...
kubectl apply -f security/falco-config.yaml
kubectl apply -f security/falco-deployment.yaml

echo.
echo 5. Istio 서비스 메시 설정...
kubectl apply -f service-mesh/istio-gateway.yaml

echo.
echo 6. KEDA 이벤트 기반 자동 스케일링 배포...
kubectl apply -f scaling/keda-scaledobjects.yaml

echo.
echo 7. 보안 정책 적용...
kubectl apply -f security/network-policies.yaml

echo.
echo 8. 서비스 상태 확인...
kubectl get pods -n restaurant-system
kubectl get pods -n monitoring

echo.
echo 9. 보안 모니터링 대시보드 접속 정보...
echo OPA 대시보드: http://localhost:8181
echo Falco 대시보드: http://localhost:9376
echo Istio Kiali: http://localhost:20001

echo.
echo ========================================
echo Phase 10-4 배포 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. 보안 정책 테스트
echo 2. 성능 모니터링 확인
echo 3. 자동 스케일링 테스트
echo.
pause 