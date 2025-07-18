#!/usr/bin/env python3
"""
플러그인 모니터링 및 로깅 시스템 통합 테스트
모든 기능이 정상적으로 작동하는지 확인
"""

import asyncio
import time
import random
import tempfile
import shutil
from pathlib import Path
import json
import psutil
import logging
from typing import Optional

# 테스트 대상 모듈들
from plugin_monitoring import PluginMonitor, PluginMetrics
from plugin_logging import PluginLogManager
from plugin_monitoring_dashboard import PluginMonitoringDashboard, DashboardConfig

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringSystemTest:
    """모니터링 시스템 통합 테스트 클래스"""

    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="plugin_monitoring_test_"))
        self.monitor_db = self.test_dir / "test_monitoring.db"
        self.log_db = self.test_dir / "test_logs.db"

        self.monitor: Optional[PluginMonitor] = None
        self.log_manager: Optional[PluginLogManager] = None
        self.dashboard: Optional[PluginMonitoringDashboard] = None

        self.test_results = {
            "monitoring": {},
            "logging": {},
            "dashboard": {},
            "integration": {},
        }

    def setup(self):
        """테스트 환경 설정"""
        logger.info("테스트 환경 설정 중...")

        try:
            # 모니터링 시스템 초기화
            self.monitor = PluginMonitor(str(self.monitor_db))
            self.monitor.start_monitoring()

            # 로깅 시스템 초기화
            self.log_manager = PluginLogManager(str(self.log_db))

            # 대시보드 초기화
            config = DashboardConfig(
                host="localhost",
                port=8081,  # 테스트용 포트
                refresh_interval=5,
                enable_websocket=True,
                enable_notifications=True,
            )
            self.dashboard = PluginMonitoringDashboard(config)
            self.dashboard.set_monitoring_components(self.monitor, self.log_manager)

            logger.info("테스트 환경 설정 완료")
            return True

        except Exception as e:
            logger.error(f"테스트 환경 설정 실패: {e}")
            return False

    def cleanup(self):
        """테스트 환경 정리"""
        logger.info("테스트 환경 정리 중...")

        try:
            if self.dashboard:
                self.dashboard.stop_dashboard()

            if self.monitor:
                self.monitor.stop_monitoring()

            if self.log_manager:
                self.log_manager.shutdown()

            # 테스트 디렉토리 삭제
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)

            logger.info("테스트 환경 정리 완료")

        except Exception as e:
            logger.error(f"테스트 환경 정리 실패: {e}")

    def test_monitoring_system(self):
        """모니터링 시스템 테스트"""
        logger.info("=== 모니터링 시스템 테스트 시작 ===")

        # 타입 안전성 보장
        assert self.monitor is not None, "모니터링 시스템이 초기화되지 않았습니다"

        try:
            # 1. 메트릭 기록 테스트
            logger.info("1. 메트릭 기록 테스트")
            test_metrics = []

            for i in range(10):
                metric = PluginMetrics(
                    plugin_id=f"test_plugin_{i % 3}",
                    execution_time=random.uniform(0.1, 5.0),
                    memory_usage=random.uniform(10, 200),
                    cpu_usage=random.uniform(5, 80),
                    success=random.random() > 0.1,  # 90% 성공률
                    error_message=None if random.random() > 0.1 else "테스트 오류",
                    metadata={"test_iteration": i},
                )
                test_metrics.append(metric)
                self.monitor.record_metrics(metric)
                time.sleep(0.1)

            # 데이터베이스 플러시 대기
            time.sleep(2)

            # 메트릭 조회 테스트
            for plugin_id in ["test_plugin_0", "test_plugin_1", "test_plugin_2"]:
                metrics = self.monitor.get_plugin_metrics(plugin_id, 1)
                assert len(metrics) > 0, f"플러그인 {plugin_id}의 메트릭이 없습니다"

                summary = self.monitor.get_performance_summary(plugin_id, 1)
                assert (
                    summary["total_executions"] > 0
                ), f"플러그인 {plugin_id}의 실행 기록이 없습니다"

            self.test_results["monitoring"]["metrics_recording"] = "PASS"
            logger.info("✓ 메트릭 기록 테스트 통과")

            # 2. 알림 시스템 테스트
            logger.info("2. 알림 시스템 테스트")

            # 임계값 초과 메트릭 생성
            alert_metric = PluginMetrics(
                plugin_id="alert_test_plugin",
                execution_time=60.0,  # 임계값 초과
                memory_usage=1024.0,  # 임계값 초과
                cpu_usage=95.0,  # 임계값 초과
                success=False,
                error_message="알림 테스트 오류",
            )

            self.monitor.record_metrics(alert_metric)
            time.sleep(2)  # 알림 처리 대기

            # 알림 확인
            alerts = self.monitor.get_active_alerts()
            assert len(alerts) > 0, "알림이 생성되지 않았습니다"

            self.test_results["monitoring"]["alert_system"] = "PASS"
            logger.info("✓ 알림 시스템 테스트 통과")

            # 3. 임계값 업데이트 테스트
            logger.info("3. 임계값 업데이트 테스트")

            original_threshold = self.monitor.thresholds["execution_time"]
            self.monitor.update_thresholds(execution_time=10.0)

            assert (
                self.monitor.thresholds["execution_time"] == 10.0
            ), "임계값 업데이트가 실패했습니다"

            # 원래 값으로 복원
            self.monitor.update_thresholds(execution_time=original_threshold)

            self.test_results["monitoring"]["threshold_update"] = "PASS"
            logger.info("✓ 임계값 업데이트 테스트 통과")

            logger.info("=== 모니터링 시스템 테스트 완료 ===")
            return True

        except Exception as e:
            logger.error(f"모니터링 시스템 테스트 실패: {e}")
            self.test_results["monitoring"]["error"] = str(e)
            return False

    def test_logging_system(self):
        """로깅 시스템 테스트"""
        logger.info("=== 로깅 시스템 테스트 시작 ===")

        # 타입 안전성 보장
        assert self.log_manager is not None, "로깅 시스템이 초기화되지 않았습니다"

        try:
            # 1. 로거 생성 및 로그 기록 테스트
            logger.info("1. 로거 생성 및 로그 기록 테스트")

            test_loggers = []
            for i in range(3):
                plugin_logger = self.log_manager.get_logger(f"test_plugin_{i}")
                test_loggers.append(plugin_logger)

                # 다양한 레벨의 로그 기록
                plugin_logger.debug(f"디버그 메시지 {i}")
                plugin_logger.info(f"정보 메시지 {i}")
                plugin_logger.warning(f"경고 메시지 {i}")

                if i % 2 == 0:  # 일부 플러그인에서 오류 발생
                    plugin_logger.error(f"오류 메시지 {i}")
                    plugin_logger.exception(f"예외 메시지 {i}")

            # 로그 조회 테스트
            for i in range(3):
                plugin_id = f"test_plugin_{i}"
                logs = self.log_manager.get_logs(plugin_id=plugin_id)
                assert len(logs) > 0, f"플러그인 {plugin_id}의 로그가 없습니다"

            self.test_results["logging"]["log_recording"] = "PASS"
            logger.info("✓ 로그 기록 테스트 통과")

            # 2. 로그 검색 테스트
            logger.info("2. 로그 검색 테스트")

            search_results = self.log_manager.search_logs("오류")
            assert len(search_results) > 0, "오류 로그 검색 결과가 없습니다"

            self.test_results["logging"]["log_search"] = "PASS"
            logger.info("✓ 로그 검색 테스트 통과")

            # 3. 로그 통계 테스트
            logger.info("3. 로그 통계 테스트")

            stats = self.log_manager.get_log_statistics(days=1)
            assert stats["total_logs"] > 0, "로그 통계가 없습니다"

            self.test_results["logging"]["log_statistics"] = "PASS"
            logger.info("✓ 로그 통계 테스트 통과")

            # 4. 로그 패턴 분석 테스트
            logger.info("4. 로그 패턴 분석 테스트")

            # 패턴 추가
            self.log_manager.add_log_pattern(
                pattern=r"오류 메시지 \d+",
                description="테스트 오류 패턴",
                severity="ERROR",
            )

            patterns = self.log_manager.analyze_log_patterns(hours=1)
            assert len(patterns) > 0, "로그 패턴 분석 결과가 없습니다"

            self.test_results["logging"]["log_patterns"] = "PASS"
            logger.info("✓ 로그 패턴 분석 테스트 통과")

            # 5. 로그 내보내기 테스트
            logger.info("5. 로그 내보내기 테스트")

            export_path = self.test_dir / "test_logs_export.json"
            self.log_manager.export_logs(str(export_path), format="json")

            assert export_path.exists(), "로그 내보내기 파일이 생성되지 않았습니다"

            # 내보낸 파일 확인
            with open(export_path, "r", encoding="utf-8") as f:
                exported_data = json.load(f)
                assert len(exported_data) > 0, "내보낸 로그 데이터가 없습니다"

            self.test_results["logging"]["log_export"] = "PASS"
            logger.info("✓ 로그 내보내기 테스트 통과")

            logger.info("=== 로깅 시스템 테스트 완료 ===")
            return True

        except Exception as e:
            logger.error(f"로깅 시스템 테스트 실패: {e}")
            self.test_results["logging"]["error"] = str(e)
            return False

    def test_dashboard_system(self):
        """대시보드 시스템 테스트"""
        logger.info("=== 대시보드 시스템 테스트 시작 ===")

        # 타입 안전성 보장
        assert self.dashboard is not None, "대시보드 시스템이 초기화되지 않았습니다"

        try:
            # 1. 대시보드 초기화 테스트
            logger.info("1. 대시보드 초기화 테스트")

            assert self.dashboard is not None, "대시보드가 초기화되지 않았습니다"
            assert (
                self.dashboard.monitor is not None
            ), "모니터링 컴포넌트가 연결되지 않았습니다"
            assert (
                self.dashboard.log_manager is not None
            ), "로깅 컴포넌트가 연결되지 않았습니다"

            self.test_results["dashboard"]["initialization"] = "PASS"
            logger.info("✓ 대시보드 초기화 테스트 통과")

            # 2. 플러그인 상태 업데이트 테스트
            logger.info("2. 플러그인 상태 업데이트 테스트")

            # 테스트 메트릭으로 상태 업데이트
            test_metric = PluginMetrics(
                plugin_id="dashboard_test_plugin",
                execution_time=2.5,
                memory_usage=150.0,
                cpu_usage=45.0,
                success=True,
                metadata={"test": "dashboard"},
            )

            self.dashboard.update_plugin_status("dashboard_test_plugin", test_metric)

            # 상태 확인
            status = self.dashboard.plugin_status.get("dashboard_test_plugin")
            assert status is not None, "플러그인 상태가 업데이트되지 않았습니다"
            assert status.execution_count == 1, "실행 횟수가 올바르지 않습니다"

            self.test_results["dashboard"]["status_update"] = "PASS"
            logger.info("✓ 플러그인 상태 업데이트 테스트 통과")

            # 3. API 엔드포인트 테스트
            logger.info("3. API 엔드포인트 테스트")

            # 상태 API 테스트
            status_data = asyncio.run(self.dashboard._get_current_status())
            assert "plugins" in status_data, "상태 API 응답에 플러그인 정보가 없습니다"

            self.test_results["dashboard"]["api_endpoints"] = "PASS"
            logger.info("✓ API 엔드포인트 테스트 통과")

            logger.info("=== 대시보드 시스템 테스트 완료 ===")
            return True

        except Exception as e:
            logger.error(f"대시보드 시스템 테스트 실패: {e}")
            self.test_results["dashboard"]["error"] = str(e)
            return False

    def test_integration(self):
        """통합 테스트"""
        logger.info("=== 통합 테스트 시작 ===")

        # 타입 안전성 보장
        assert self.monitor is not None, "모니터링 시스템이 초기화되지 않았습니다"
        assert self.log_manager is not None, "로깅 시스템이 초기화되지 않았습니다"
        assert self.dashboard is not None, "대시보드 시스템이 초기화되지 않았습니다"

        try:
            # 1. 모니터링-로깅 연동 테스트
            logger.info("1. 모니터링-로깅 연동 테스트")

            # 플러그인 로거 생성
            plugin_logger = self.log_manager.get_logger("integration_test_plugin")

            # 메트릭 기록 (로깅 포함)
            metric = PluginMetrics(
                plugin_id="integration_test_plugin",
                execution_time=3.0,
                memory_usage=100.0,
                cpu_usage=30.0,
                success=True,
                metadata={"integration_test": True},
            )

            # 모니터링에 메트릭 기록
            self.monitor.record_metrics(metric)

            # 로깅에 실행 로그 기록 (정의된 필드만 전달)
            plugin_logger.info(
                "통합 테스트 실행 완료",
                context={"execution_time": 3.0, "memory_usage": 100.0},
            )

            # 데이터 확인
            if self.monitor:
                metrics = self.monitor.get_plugin_metrics("integration_test_plugin", 1)
            else:
                metrics = []
            if self.log_manager:
                logs = self.log_manager.get_logs(plugin_id="integration_test_plugin")
            else:
                logs = []

            assert len(metrics) > 0, "통합 테스트 메트릭이 없습니다"
            assert len(logs) > 0, "통합 테스트 로그가 없습니다"

            self.test_results["integration"]["monitoring_logging"] = "PASS"
            logger.info("✓ 모니터링-로깅 연동 테스트 통과")

            # 2. 대시보드 통합 테스트
            logger.info("2. 대시보드 통합 테스트")

            # 대시보드 상태 업데이트
            self.dashboard.update_plugin_status("integration_test_plugin", metric)

            # 대시보드 상태 확인
            status = self.dashboard.plugin_status.get("integration_test_plugin")
            assert status is not None, "대시보드에 플러그인 상태가 반영되지 않았습니다"

            self.test_results["integration"]["dashboard_integration"] = "PASS"
            logger.info("✓ 대시보드 통합 테스트 통과")

            # 3. 실시간 업데이트 테스트
            logger.info("3. 실시간 업데이트 테스트")

            # 여러 메트릭을 연속으로 기록
            for i in range(5):
                metric = PluginMetrics(
                    plugin_id="realtime_test_plugin",
                    execution_time=random.uniform(1.0, 5.0),
                    memory_usage=random.uniform(50, 200),
                    cpu_usage=random.uniform(10, 60),
                    success=random.random() > 0.2,
                    metadata={"iteration": i},
                )

                self.monitor.record_metrics(metric)
                self.dashboard.update_plugin_status("realtime_test_plugin", metric)
                time.sleep(0.2)

            # 최종 상태 확인
            final_status = self.dashboard.plugin_status.get("realtime_test_plugin")
            assert final_status is not None, "실시간 업데이트가 작동하지 않습니다"
            assert final_status.execution_count == 5, "실행 횟수가 올바르지 않습니다"

            self.test_results["integration"]["realtime_updates"] = "PASS"
            logger.info("✓ 실시간 업데이트 테스트 통과")

            logger.info("=== 통합 테스트 완료 ===")
            return True

        except Exception as e:
            logger.error(f"통합 테스트 실패: {e}")
            self.test_results["integration"]["error"] = str(e)
            return False

    def test_performance(self):
        """성능 테스트"""
        logger.info("=== 성능 테스트 시작 ===")

        # 타입 안전성 보장
        assert self.monitor is not None, "모니터링 시스템이 초기화되지 않았습니다"
        assert self.log_manager is not None, "로깅 시스템이 초기화되지 않았습니다"
        assert self.dashboard is not None, "대시보드 시스템이 초기화되지 않았습니다"

        try:
            # 1. 대량 메트릭 처리 테스트
            logger.info("1. 대량 메트릭 처리 테스트")

            start_time = time.time()

            # 1000개의 메트릭을 빠르게 기록
            for i in range(1000):
                metric = PluginMetrics(
                    plugin_id=f"perf_test_plugin_{i % 10}",
                    execution_time=random.uniform(0.1, 2.0),
                    memory_usage=random.uniform(10, 100),
                    cpu_usage=random.uniform(5, 50),
                    success=random.random() > 0.05,
                    metadata={"performance_test": True, "index": i},
                )

                self.monitor.record_metrics(metric)

            end_time = time.time()
            processing_time = end_time - start_time

            logger.info(f"1000개 메트릭 처리 시간: {processing_time:.2f}초")
            assert (
                processing_time < 10.0
            ), f"메트릭 처리 시간이 너무 깁니다: {processing_time}초"

            self.test_results["performance"]["bulk_metrics"] = "PASS"
            logger.info("✓ 대량 메트릭 처리 테스트 통과")

            # 2. 대량 로그 처리 테스트
            logger.info("2. 대량 로그 처리 테스트")

            start_time = time.time()

            # 1000개의 로그를 빠르게 기록
            for i in range(1000):
                plugin_logger = self.log_manager.get_logger(f"perf_log_plugin_{i % 10}")
                plugin_logger.info(f"성능 테스트 로그 {i}", iteration=i)

            end_time = time.time()
            processing_time = end_time - start_time

            logger.info(f"1000개 로그 처리 시간: {processing_time:.2f}초")
            assert (
                processing_time < 15.0
            ), f"로그 처리 시간이 너무 깁니다: {processing_time}초"

            self.test_results["performance"]["bulk_logs"] = "PASS"
            logger.info("✓ 대량 로그 처리 테스트 통과")

            # 3. 메모리 사용량 테스트
            logger.info("3. 메모리 사용량 테스트")

            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB

            logger.info(f"현재 메모리 사용량: {memory_usage:.2f}MB")
            assert (
                memory_usage < 500
            ), f"메모리 사용량이 너무 높습니다: {memory_usage}MB"

            self.test_results["performance"]["memory_usage"] = "PASS"
            logger.info("✓ 메모리 사용량 테스트 통과")

            logger.info("=== 성능 테스트 완료 ===")
            return True

        except Exception as e:
            logger.error(f"성능 테스트 실패: {e}")
            self.test_results["performance"]["error"] = str(e)
            return False

    def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("🚀 플러그인 모니터링 시스템 통합 테스트 시작")

        if not self.setup():
            logger.error("테스트 환경 설정 실패")
            return False

        try:
            # 각 시스템별 테스트 실행
            tests = [
                ("모니터링 시스템", self.test_monitoring_system),
                ("로깅 시스템", self.test_logging_system),
                ("대시보드 시스템", self.test_dashboard_system),
                ("통합 테스트", self.test_integration),
                ("성능 테스트", self.test_performance),
            ]

            all_passed = True

            for test_name, test_func in tests:
                logger.info(f"\n{'='*50}")
                logger.info(f"📋 {test_name} 테스트 실행")
                logger.info(f"{'='*50}")

                try:
                    if asyncio.iscoroutinefunction(test_func):
                        result = asyncio.run(test_func())
                    else:
                        result = test_func()

                    if result:
                        logger.info(f"✅ {test_name} 테스트 통과")
                    else:
                        logger.error(f"❌ {test_name} 테스트 실패")
                        all_passed = False

                except Exception as e:
                    logger.error(f"❌ {test_name} 테스트 중 오류 발생: {e}")
                    all_passed = False

            # 테스트 결과 요약
            self.print_test_summary()

            return all_passed

        finally:
            self.cleanup()

    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        logger.info(f"\n{'='*60}")
        logger.info("📊 테스트 결과 요약")
        logger.info(f"{'='*60}")

        total_tests = 0
        passed_tests = 0

        for system, results in self.test_results.items():
            logger.info(f"\n�� {system.upper()} 시스템:")

            for test_name, result in results.items():
                total_tests += 1
                if result == "PASS":
                    passed_tests += 1
                    logger.info(f"  ✅ {test_name}: PASS")
                else:
                    logger.info(f"  ❌ {test_name}: {result}")

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info(f"\n📈 전체 결과:")
        logger.info(f"  총 테스트: {total_tests}개")
        logger.info(f"  통과: {passed_tests}개")
        logger.info(f"  실패: {total_tests - passed_tests}개")
        logger.info(f"  성공률: {success_rate:.1f}%")

        if success_rate >= 90:
            logger.info("🎉 테스트가 성공적으로 완료되었습니다!")
        else:
            logger.warning("⚠️ 일부 테스트가 실패했습니다.")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="플러그인 모니터링 시스템 통합 테스트")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세한 로그 출력")
    parser.add_argument(
        "--performance-only", action="store_true", help="성능 테스트만 실행"
    )
    parser.add_argument(
        "--monitoring-only", action="store_true", help="모니터링 테스트만 실행"
    )
    parser.add_argument(
        "--logging-only", action="store_true", help="로깅 테스트만 실행"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 테스트 실행
    tester = MonitoringSystemTest()

    if args.performance_only:
        tester.setup()
        try:
            tester.test_performance()
        finally:
            tester.cleanup()
    elif args.monitoring_only:
        tester.setup()
        try:
            tester.test_monitoring_system()
        finally:
            tester.cleanup()
    elif args.logging_only:
        tester.setup()
        try:
            tester.test_logging_system()
        finally:
            tester.cleanup()
    else:
        # 전체 테스트 실행
        success = tester.run_all_tests()
        exit(0 if success else 1)


if __name__ == "__main__":
    main()
