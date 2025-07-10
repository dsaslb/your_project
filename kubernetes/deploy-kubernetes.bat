@echo off
echo ========================================
echo 레스토랑 관리 시스템 Kubernetes 배포
echo ========================================

echo.
echo 1. 네임스페이스 생성...
kubectl apply -f namespaces/restaurant-system.yaml

echo.
echo 2. ConfigMap 및 Secret 생성...
kubectl apply -f configmaps/app-config.yaml
kubectl apply -f secrets/app-secrets.yaml

echo.
echo 3. 애플리케이션 서비스 배포...
kubectl apply -f deployments/gateway-deployment.yaml
kubectl apply -f deployments/user-deployment.yaml
kubectl apply -f deployments/iot-deployment.yaml

echo.
echo 4. 서비스 생성...
kubectl apply -f services/app-services.yaml

echo.
echo 5. Ingress 생성...
kubectl apply -f ingress/app-ingress.yaml

echo.
echo 6. 모니터링 시스템 배포...
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/grafana-datasources.yaml
kubectl apply -f monitoring/grafana-deployment.yaml

echo.
echo 7. 배포 상태 확인...
timeout /t 10 /nobreak > nul
kubectl get pods -n restaurant-system
kubectl get pods -n monitoring

echo.
echo 8. 서비스 상태 확인...
kubectl get services -n restaurant-system
kubectl get services -n monitoring

echo.
echo 9. Ingress 상태 확인...
kubectl get ingress -n restaurant-system
kubectl get ingress -n monitoring

echo.
echo ========================================
echo Kubernetes 배포 완료!
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
echo - kubectl get pods -n restaurant-system
echo - kubectl logs -f deployment/gateway-deployment -n restaurant-system
echo.
echo 배포 제거:
echo - kubectl delete namespace restaurant-system
echo - kubectl delete namespace monitoring 