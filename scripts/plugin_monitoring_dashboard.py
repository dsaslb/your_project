#!/usr/bin/env python3
"""
플러그인 모니터링 대시보드
실시간 상태 확인, 성능 분석, 알림 관리 통합 시스템
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import io
from collections import defaultdict, deque
import aiohttp
from aiohttp import web
import jinja2

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """대시보드 설정"""

    host: str = "localhost"
    port: int = 8080
    refresh_interval: int = 30  # 초
    max_data_points: int = 1000
    alert_check_interval: int = 60  # 초
    enable_websocket: bool = True
    enable_notifications: bool = True


@dataclass
class PluginStatus:
    """플러그인 상태 정보"""

    plugin_id: str
    is_active: bool
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    avg_memory_usage: float = 0.0
    avg_cpu_usage: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None


class PluginMonitoringDashboard:
    """플러그인 모니터링 대시보드"""

    def __init__(self, config: DashboardConfig):
        self.config = config
        self.monitor = None
        self.log_manager = None
        self.plugin_status: Dict[str, PluginStatus] = {}
        self.performance_data: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=config.max_data_points)
        )
        self.alert_history: List[Dict[str, Any]] = []
        self.websocket_clients: List[web.WebSocketResponse] = []
        self.dashboard_running = False
        self.update_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # 템플릿 환경 설정
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"), autoescape=True
        )

        # 웹 애플리케이션 설정
        self.app = web.Application()
        self.setup_routes()

    def set_monitoring_components(self, monitor, log_manager):
        """모니터링 컴포넌트 설정"""
        self.monitor = monitor
        self.log_manager = log_manager

        # 알림 콜백 등록
        if self.monitor:
            self.monitor.add_alert_callback(self._handle_alert)

    def setup_routes(self):
        """웹 라우트 설정"""
        self.app.router.add_get("/", self.dashboard_page)
        self.app.router.add_get("/api/status", self.api_status)
        self.app.router.add_get("/api/performance/{plugin_id}", self.api_performance)
        self.app.router.add_get("/api/logs/{plugin_id}", self.api_logs)
        self.app.router.add_get("/api/alerts", self.api_alerts)
        self.app.router.add_get("/api/statistics", self.api_statistics)
        self.app.router.add_get("/api/chart/{plugin_id}", self.api_chart)
        self.app.router.add_post(
            "/api/alert/resolve/{alert_id}", self.api_resolve_alert
        )
        self.app.router.add_get("/ws", self.websocket_handler)

        # 정적 파일 서빙
        self.app.router.add_static("/static", path="static", name="static")

    async def dashboard_page(self, request):
        """대시보드 메인 페이지"""
        try:
            template = self.template_env.get_template("plugin_dashboard.html")
            context = {
                "title": "플러그인 모니터링 대시보드",
                "refresh_interval": self.config.refresh_interval * 1000,
                "enable_websocket": self.config.enable_websocket,
            }
            html = template.render(**context)
            return web.Response(text=html, content_type="text/html")
        except Exception as e:
            logger.error(f"대시보드 페이지 로드 실패: {e}")
            return web.Response(text="대시보드 로드 실패", status=500)

    async def api_status(self, request):
        """플러그인 상태 API"""
        try:
            status_data = []
            for plugin_id, status in self.plugin_status.items():
                status_data.append(
                    {
                        "plugin_id": plugin_id,
                        "is_active": status.is_active,
                        "last_execution": (
                            status.last_execution.isoformat()
                            if status.last_execution
                            else None
                        ),
                        "execution_count": status.execution_count,
                        "success_rate": status.success_rate,
                        "avg_execution_time": status.avg_execution_time,
                        "avg_memory_usage": status.avg_memory_usage,
                        "avg_cpu_usage": status.avg_cpu_usage,
                        "error_count": status.error_count,
                        "warning_count": status.warning_count,
                        "last_error": status.last_error,
                        "last_error_time": (
                            status.last_error_time.isoformat()
                            if status.last_error_time
                            else None
                        ),
                    }
                )

            return web.json_response(
                {
                    "status": "success",
                    "data": status_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"상태 API 오류: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def api_performance(self, request):
        """플러그인 성능 데이터 API"""
        try:
            plugin_id = request.match_info["plugin_id"]
            hours = int(request.query.get("hours", 24))

            if self.monitor:
                metrics = self.monitor.get_plugin_metrics(plugin_id, hours)
                performance_data = []

                for metric in metrics:
                    performance_data.append(
                        {
                            "timestamp": metric.timestamp.isoformat(),
                            "execution_time": metric.execution_time,
                            "memory_usage": metric.memory_usage,
                            "cpu_usage": metric.cpu_usage,
                            "success": metric.success,
                        }
                    )

                return web.json_response(
                    {"status": "success", "data": performance_data}
                )
            else:
                return web.json_response(
                    {
                        "status": "error",
                        "message": "모니터링 시스템이 초기화되지 않았습니다",
                    },
                    status=500,
                )

        except Exception as e:
            logger.error(f"성능 API 오류: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def api_logs(self, request):
        """플러그인 로그 API"""
        try:
            plugin_id = request.match_info["plugin_id"]
            level = request.query.get("level")
            limit = int(request.query.get("limit", 100))

            if self.log_manager:
                logs = self.log_manager.get_logs(
                    plugin_id=plugin_id, level=level, limit=limit
                )
                log_data = []

                for log in logs:
                    log_data.append(
                        {
                            "timestamp": log.timestamp.isoformat(),
                            "level": log.level,
                            "message": log.message,
                            "module": log.module,
                            "function": log.function,
                            "line_number": log.line_number,
                            "exception_info": log.exception_info,
                            "trace_id": log.trace_id,
                        }
                    )

                return web.json_response({"status": "success", "data": log_data})
            else:
                return web.json_response(
                    {
                        "status": "error",
                        "message": "로그 시스템이 초기화되지 않았습니다",
                    },
                    status=500,
                )

        except Exception as e:
            logger.error(f"로그 API 오류: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def api_alerts(self, request):
        """알림 API"""
        try:
            severity = request.query.get("severity")
            limit = int(request.query.get("limit", 50))

            if self.monitor:
                alerts = self.monitor.get_active_alerts(severity)
                alert_data = []

                for alert in alerts[:limit]:
                    alert_data.append(
                        {
                            "id": id(alert),  # 임시 ID
                            "plugin_id": alert.plugin_id,
                            "alert_type": alert.alert_type,
                            "severity": alert.severity,
                            "message": alert.message,
                            "threshold": alert.threshold,
                            "current_value": alert.current_value,
                            "timestamp": alert.timestamp.isoformat(),
                        }
                    )

                return web.json_response({"status": "success", "data": alert_data})
            else:
                return web.json_response(
                    {
                        "status": "error",
                        "message": "모니터링 시스템이 초기화되지 않았습니다",
                    },
                    status=500,
                )

        except Exception as e:
            logger.error(f"알림 API 오류: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def api_statistics(self, request):
        """통계 API"""
        try:
            days = int(request.query.get("days", 7))

            stats = {}

            if self.log_manager:
                log_stats = self.log_manager.get_log_statistics(days=days)
                stats["logs"] = log_stats

            if self.monitor:
                # 성능 통계 계산
                performance_stats = {}
                for plugin_id in self.plugin_status.keys():
                    summary = self.monitor.get_performance_summary(plugin_id, days * 24)
                    performance_stats[plugin_id] = summary

                stats["performance"] = performance_stats

            return web.json_response({"status": "success", "data": stats})

        except Exception as e:
            logger.error(f"통계 API 오류: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def api_chart(self, request):
        """차트 이미지 API"""
        try:
            plugin_id = request.match_info["plugin_id"]
            chart_type = request.query.get("type", "performance")
            hours = int(request.query.get("hours", 24))

            if self.monitor:
                metrics = self.monitor.get_plugin_metrics(plugin_id, hours)

                if not metrics:
                    return web.Response(text="데이터가 없습니다", status=404)

                # 차트 생성
                fig = self._create_performance_chart(metrics, chart_type)

                # 이미지를 바이트로 변환
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format="png", dpi=100, bbox_inches="tight")
                img_buffer.seek(0)

                return web.Response(
                    body=img_buffer.getvalue(), content_type="image/png"
                )
            else:
                return web.Response(
                    text="모니터링 시스템이 초기화되지 않았습니다", status=500
                )

        except Exception as e:
            logger.error(f"차트 API 오류: {e}")
            return web.Response(text=str(e), status=500)

    def _create_performance_chart(self, metrics: List, chart_type: str) -> Figure:
        """성능 차트 생성"""
        fig, ax = plt.subplots(figsize=(10, 6))

        timestamps = [m.timestamp for m in metrics]

        if chart_type == "execution_time":
            values = [m.execution_time for m in metrics]
            ax.set_ylabel("실행 시간 (초)")
            ax.set_title("플러그인 실행 시간 추이")
        elif chart_type == "memory_usage":
            values = [m.memory_usage for m in metrics]
            ax.set_ylabel("메모리 사용량 (MB)")
            ax.set_title("플러그인 메모리 사용량 추이")
        elif chart_type == "cpu_usage":
            values = [m.cpu_usage for m in metrics]
            ax.set_ylabel("CPU 사용량 (%)")
            ax.set_title("플러그인 CPU 사용량 추이")
        else:
            values = [m.execution_time for m in metrics]
            ax.set_ylabel("실행 시간 (초)")
            ax.set_title("플러그인 성능 추이")

        ax.plot(timestamps, values, marker="o", linestyle="-", markersize=3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_major_locator(
            mdates.HourLocator(interval=max(1, len(timestamps) // 10))
        )
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig

    async def api_resolve_alert(self, request):
        """알림 해결 API"""
        try:
            alert_id = int(request.match_info["alert_id"])

            if self.monitor:
                self.monitor.resolve_alert(alert_id)
                return web.json_response({"status": "success"})
            else:
                return web.json_response(
                    {
                        "status": "error",
                        "message": "모니터링 시스템이 초기화되지 않았습니다",
                    },
                    status=500,
                )

        except Exception as e:
            logger.error(f"알림 해결 API 오류: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def websocket_handler(self, request):
        """웹소켓 핸들러"""
        if not self.config.enable_websocket:
            return web.Response(text="웹소켓이 비활성화되어 있습니다", status=400)

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websocket_clients.append(ws)

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._handle_websocket_message(ws, data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"웹소켓 오류: {ws.exception()}")
        except Exception as e:
            logger.error(f"웹소켓 처리 오류: {e}")
        finally:
            if ws in self.websocket_clients:
                self.websocket_clients.remove(ws)

        return ws

    async def _handle_websocket_message(self, ws, data):
        """웹소켓 메시지 처리"""
        try:
            message_type = data.get("type")

            if message_type == "subscribe":
                # 구독 처리
                await ws.send_json(
                    {"type": "subscribed", "data": {"message": "구독이 완료되었습니다"}}
                )
            elif message_type == "get_status":
                # 상태 정보 전송
                status_data = await self._get_current_status()
                await ws.send_json({"type": "status_update", "data": status_data})
        except Exception as e:
            logger.error(f"웹소켓 메시지 처리 오류: {e}")

    async def _get_current_status(self) -> Dict[str, Any]:
        """현재 상태 정보 조회"""
        status_data = []
        for plugin_id, status in self.plugin_status.items():
            status_data.append(
                {
                    "plugin_id": plugin_id,
                    "is_active": status.is_active,
                    "last_execution": (
                        status.last_execution.isoformat()
                        if status.last_execution
                        else None
                    ),
                    "execution_count": status.execution_count,
                    "success_rate": status.success_rate,
                    "avg_execution_time": status.avg_execution_time,
                    "error_count": status.error_count,
                }
            )

        return {"plugins": status_data, "timestamp": datetime.now().isoformat()}

    def _handle_alert(self, alert):
        """알림 처리"""
        alert_data = {
            "id": id(alert),
            "plugin_id": alert.plugin_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "threshold": alert.threshold,
            "current_value": alert.current_value,
            "timestamp": alert.timestamp.isoformat(),
        }

        self.alert_history.append(alert_data)

        # 웹소켓 클라이언트들에게 알림 전송
        asyncio.create_task(self._broadcast_alert(alert_data))

        # 콜백 실행
        for callback in self.update_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {e}")

    async def _broadcast_alert(self, alert_data):
        """알림 브로드캐스트"""
        if not self.websocket_clients:
            return

        message = {"type": "alert", "data": alert_data}

        disconnected_clients = []
        for ws in self.websocket_clients:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"웹소켓 알림 전송 오류: {e}")
                disconnected_clients.append(ws)

        # 연결이 끊어진 클라이언트 제거
        for ws in disconnected_clients:
            if ws in self.websocket_clients:
                self.websocket_clients.remove(ws)

    def update_plugin_status(self, plugin_id: str, metrics=None):
        """플러그인 상태 업데이트"""
        if plugin_id not in self.plugin_status:
            self.plugin_status[plugin_id] = PluginStatus(
                plugin_id=plugin_id, is_active=True
            )

        status = self.plugin_status[plugin_id]

        if metrics:
            status.last_execution = metrics.timestamp
            status.execution_count += 1

            if metrics.success:
                status.success_rate = (
                    status.success_rate * (status.execution_count - 1) + 1
                ) / status.execution_count
            else:
                status.success_rate = (
                    status.success_rate * (status.execution_count - 1)
                ) / status.execution_count
                status.error_count += 1
                status.last_error = metrics.error_message
                status.last_error_time = metrics.timestamp

            # 평균값 업데이트
            if status.execution_count == 1:
                status.avg_execution_time = metrics.execution_time
                status.avg_memory_usage = metrics.memory_usage
                status.avg_cpu_usage = metrics.cpu_usage
            else:
                status.avg_execution_time = (
                    status.avg_execution_time * (status.execution_count - 1)
                    + metrics.execution_time
                ) / status.execution_count
                status.avg_memory_usage = (
                    status.avg_memory_usage * (status.execution_count - 1)
                    + metrics.memory_usage
                ) / status.execution_count
                status.avg_cpu_usage = (
                    status.avg_cpu_usage * (status.execution_count - 1)
                    + metrics.cpu_usage
                ) / status.execution_count

        # 성능 데이터 저장
        if metrics:
            self.performance_data[plugin_id].append(
                {
                    "timestamp": metrics.timestamp,
                    "execution_time": metrics.execution_time,
                    "memory_usage": metrics.memory_usage,
                    "cpu_usage": metrics.cpu_usage,
                    "success": metrics.success,
                }
            )

    def add_update_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """업데이트 콜백 추가"""
        self.update_callbacks.append(callback)

    async def start_dashboard(self):
        """대시보드 시작"""
        if self.dashboard_running:
            logger.warning("대시보드가 이미 실행 중입니다")
            return

        self.dashboard_running = True

        # 백그라운드 업데이트 태스크 시작
        asyncio.create_task(self._background_update_loop())

        # 웹 서버 시작
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, self.config.host, self.config.port)
        await site.start()

        logger.info(
            f"플러그인 모니터링 대시보드가 시작되었습니다: http://{self.config.host}:{self.config.port}"
        )

        try:
            # 서버 실행 유지
            while self.dashboard_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("대시보드 종료 신호 수신")
        finally:
            await runner.cleanup()
            self.dashboard_running = False

    async def _background_update_loop(self):
        """백그라운드 업데이트 루프"""
        while self.dashboard_running:
            try:
                # 플러그인 상태 업데이트
                if self.monitor:
                    for plugin_id in self.plugin_status.keys():
                        summary = self.monitor.get_performance_summary(
                            plugin_id, 1
                        )  # 최근 1시간
                        if summary["total_executions"] > 0:
                            status = self.plugin_status[plugin_id]
                            status.success_rate = summary["success_rate"]
                            status.avg_execution_time = summary["avg_execution_time"]
                            status.avg_memory_usage = summary["avg_memory_usage"]
                            status.avg_cpu_usage = summary["avg_cpu_usage"]
                            status.error_count = summary["error_count"]

                # 웹소켓 클라이언트들에게 상태 업데이트 전송
                if self.websocket_clients:
                    status_data = await self._get_current_status()
                    await self._broadcast_status_update(status_data)

                await asyncio.sleep(self.config.refresh_interval)

            except Exception as e:
                logger.error(f"백그라운드 업데이트 오류: {e}")
                await asyncio.sleep(10)

    async def _broadcast_status_update(self, status_data):
        """상태 업데이트 브로드캐스트"""
        message = {"type": "status_update", "data": status_data}

        disconnected_clients = []
        for ws in self.websocket_clients:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"웹소켓 상태 업데이트 전송 오류: {e}")
                disconnected_clients.append(ws)

        # 연결이 끊어진 클라이언트 제거
        for ws in disconnected_clients:
            if ws in self.websocket_clients:
                self.websocket_clients.remove(ws)

    def stop_dashboard(self):
        """대시보드 중지"""
        self.dashboard_running = False
        logger.info("플러그인 모니터링 대시보드가 중지되었습니다")


# CLI 인터페이스
def main():
    """CLI 메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="플러그인 모니터링 대시보드")
    parser.add_argument("--host", default="localhost", help="호스트 주소")
    parser.add_argument("--port", type=int, default=8080, help="포트 번호")
    parser.add_argument(
        "--refresh-interval", type=int, default=30, help="새로고침 간격 (초)"
    )
    parser.add_argument(
        "--monitor-db",
        default="plugin_monitoring.db",
        help="모니터링 데이터베이스 경로",
    )
    parser.add_argument(
        "--log-db", default="plugin_logs.db", help="로그 데이터베이스 경로"
    )
    parser.add_argument(
        "--disable-websocket", action="store_true", help="웹소켓 비활성화"
    )
    parser.add_argument(
        "--disable-notifications", action="store_true", help="알림 비활성화"
    )

    args = parser.parse_args()

    # 설정 생성
    config = DashboardConfig(
        host=args.host,
        port=args.port,
        refresh_interval=args.refresh_interval,
        enable_websocket=not args.disable_websocket,
        enable_notifications=not args.disable_notifications,
    )

    # 대시보드 생성
    dashboard = PluginMonitoringDashboard(config)

    # 모니터링 컴포넌트 설정
    try:
        from plugin_monitoring import PluginMonitor
        from plugin_logging import PluginLogManager

        monitor = PluginMonitor(args.monitor_db)
        log_manager = PluginLogManager(args.log_db)

        dashboard.set_monitoring_components(monitor, log_manager)

        # 모니터링 시작
        monitor.start_monitoring()

        logger.info("모니터링 컴포넌트가 초기화되었습니다")

    except ImportError as e:
        logger.warning(f"모니터링 컴포넌트를 불러올 수 없습니다: {e}")
        logger.info("대시보드만 실행됩니다")

    try:
        # 대시보드 시작
        asyncio.run(dashboard.start_dashboard())
    except KeyboardInterrupt:
        logger.info("대시보드 종료")
    finally:
        dashboard.stop_dashboard()
        if monitor:
            monitor.stop_monitoring()
        if log_manager:
            log_manager.shutdown()


if __name__ == "__main__":
    main()
