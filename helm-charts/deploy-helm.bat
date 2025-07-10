@echo off
echo ========================================
echo 레스토랑 관리 시스템 Helm 배포
echo ========================================

echo.
echo 1. Helm 저장소 추가...
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

echo.
echo 2. 의존성 업데이트...
helm dependency update

echo.
echo 3. Helm 차트 배포...
helm install restaurant-management . --namespace restaurant-system --create-namespace

echo.
echo 4. 배포 상태 확인...
timeout /t 30 /nobreak > nul
helm list -n restaurant-system
kubectl get pods -n restaurant-system
kubectl get pods -n monitoring

echo.
echo 5. 서비스 상태 확인...
kubectl get services -n restaurant-system
kubectl get services -n monitoring

echo.
echo 6. Ingress 상태 확인...
kubectl get ingress -n restaurant-system
kubectl get ingress -n monitoring

echo.
echo ========================================
echo Helm 배포 완료!
echo ========================================
echo.
echo 접근 URL:
echo - API Gateway: http://api.restaurant.local
echo - Admin Dashboard: http://admin.restaurant.local
echo - IoT Dashboard: http://iot.restaurant.local
echo - Grafana: http://grafana.restaurant.local
echo - Prometheus: http://prometheus.restaurant.local
echo.
echo 모니터링:
echo - Grafana 로그인: admin / admin123
echo - helm status restaurant-management -n restaurant-system
echo - kubectl logs -f deployment/gateway-deployment -n restaurant-system
echo.
echo 배포 제거:
echo - helm uninstall restaurant-management -n restaurant-system
echo - kubectl delete namespace restaurant-system
echo - kubectl delete namespace monitoring 