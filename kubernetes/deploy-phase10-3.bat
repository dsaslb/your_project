@echo off
echo ========================================
echo Phase 10-3: 고급 모니터링 및 분산 추적 배포
echo ========================================

echo.
echo 1. Jaeger 분산 추적 시스템 배포...
kubectl apply -f tracing/jaeger-deployment.yaml

echo.
echo 2. ELK Stack 배포...
echo 2.1 Elasticsearch 배포...
kubectl apply -f logging/elasticsearch-deployment.yaml

echo 2.2 Logstash 배포...
kubectl apply -f logging/logstash-deployment.yaml

echo 2.3 Kibana 배포...
kubectl apply -f logging/kibana-deployment.yaml

echo.
echo 3. AlertManager 알림 시스템 배포...
kubectl apply -f alerting/alertmanager-config.yaml
kubectl apply -f alerting/alertmanager-deployment.yaml

echo.
echo 4. Prometheus 알림 규칙 적용...
kubectl apply -f alerting/prometheus-rules.yaml

echo.
echo 5. Prometheus 설정 업데이트...
kubectl delete configmap prometheus-config -n monitoring
kubectl apply -f monitoring/prometheus-config.yaml
kubectl rollout restart deployment/prometheus-deployment -n monitoring

echo.
echo 6. Ingress 업데이트...
kubectl apply -f ingress/app-ingress.yaml

echo.
echo 7. 배포 상태 확인...
timeout /t 30 /nobreak > nul
kubectl get pods -n monitoring

echo.
echo 8. 서비스 상태 확인...
kubectl get services -n monitoring

echo.
echo 9. Ingress 상태 확인...
kubectl get ingress -n monitoring

echo.
echo ========================================
echo Phase 10-3 배포 완료!
echo ========================================
echo.
echo 접근 URL:
echo - Jaeger (분산 추적): http://jaeger.restaurant.local
echo - Kibana (로그 분석): http://kibana.restaurant.local
echo - AlertManager (알림): http://alertmanager.restaurant.local
echo - Grafana (대시보드): http://grafana.restaurant.local
echo - Prometheus (메트릭): http://prometheus.restaurant.local
echo.
echo 모니터링:
echo - kubectl get pods -n monitoring
echo - kubectl logs -f deployment/jaeger-deployment -n monitoring
echo - kubectl logs -f deployment/elasticsearch -n monitoring
echo.
echo 배포 제거:
echo - kubectl delete -f tracing/
echo - kubectl delete -f logging/
echo - kubectl delete -f alerting/ 