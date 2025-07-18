#!/usr/bin/env python3
"""
플러그인 로깅 시스템
구조화된 로그 관리, 로그 레벨별 필터링, 로그 분석
"""

import logging
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import sys
import traceback
from contextlib import contextmanager
import re
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """로그 엔트리 데이터 클래스"""

    plugin_id: str
    level: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    exception_info: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class PluginLogger:
    """플러그인 전용 로거 클래스"""

    def __init__(self, plugin_id: str, log_manager: "PluginLogManager"):
        self.plugin_id = plugin_id
        self.log_manager = log_manager
        self.context: Dict[str, Any] = {}
        self.trace_id: Optional[str] = None

    def set_context(self, **kwargs):
        """로그 컨텍스트 설정"""
        self.context.update(kwargs)

    def set_trace_id(self, trace_id: str):
        """트레이스 ID 설정"""
        self.trace_id = trace_id

    def _log(self, level: str, message: str, **kwargs):
        """로그 기록"""
        # 호출 스택 정보 추출
        frame = sys._getframe(2)
        module = frame.f_globals.get("__name__", "unknown")
        function = frame.f_code.co_name
        line_number = frame.f_lineno

        # 예외 정보 추출
        exception_info = None
        if sys.exc_info()[0] is not None:
            exception_info = traceback.format_exc()

        # context와 다른 필드 분리
        context_data = kwargs.pop("context", {})
        context_data.update(self.context.copy())

        log_entry = LogEntry(
            plugin_id=self.plugin_id,
            level=level,
            message=message,
            module=module,
            function=function,
            line_number=line_number,
            exception_info=exception_info,
            context=context_data,
            trace_id=self.trace_id,
            **kwargs,
        )

        self.log_manager.add_log(log_entry)

    def debug(self, message: str, **kwargs):
        """DEBUG 레벨 로그"""
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """INFO 레벨 로그"""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """WARNING 레벨 로그"""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """ERROR 레벨 로그"""
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """CRITICAL 레벨 로그"""
        self._log("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs):
        """예외 로그 (ERROR 레벨 + 예외 정보)"""
        self._log("ERROR", message, exception_info=traceback.format_exc(), **kwargs)


class PluginLogManager:
    """플러그인 로그 관리자"""

    def __init__(self, db_path: str = "plugin_logs.db", max_logs: int = 100000):
        self.db_path = db_path
        self.max_logs = max_logs
        self.loggers: Dict[str, PluginLogger] = {}
        self.log_queue: List[LogEntry] = []
        self.queue_lock = threading.Lock()
        self.flush_thread: Optional[threading.Thread] = None
        self.running = False

        # 로그 레벨 우선순위
        self.log_levels = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }

        self._init_database()
        self._start_flush_thread()

    def _init_database(self):
        """로그 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plugin_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        module TEXT,
                        function TEXT,
                        line_number INTEGER,
                        exception_info TEXT,
                        context TEXT,
                        trace_id TEXT,
                        user_id TEXT,
                        session_id TEXT
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS log_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern TEXT NOT NULL,
                        description TEXT,
                        severity TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS log_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        date DATE NOT NULL,
                        total_logs INTEGER DEFAULT 0,
                        error_count INTEGER DEFAULT 0,
                        warning_count INTEGER DEFAULT 0,
                        avg_response_time REAL DEFAULT 0,
                        unique_users INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # 인덱스 생성
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_plugin_logs_plugin_id ON plugin_logs(plugin_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_plugin_logs_timestamp ON plugin_logs(timestamp)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_plugin_logs_level ON plugin_logs(level)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_plugin_logs_trace_id ON plugin_logs(trace_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_log_analytics_plugin_date ON log_analytics(plugin_id, date)"
                )

                conn.commit()
                logger.info("로그 데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"로그 데이터베이스 초기화 실패: {e}")

    def _start_flush_thread(self):
        """로그 플러시 스레드 시작"""
        self.running = True
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()

    def _flush_loop(self):
        """로그 플러시 루프"""
        while self.running:
            try:
                with self.queue_lock:
                    if self.log_queue:
                        logs_to_flush = self.log_queue.copy()
                        self.log_queue.clear()
                    else:
                        logs_to_flush = []

                if logs_to_flush:
                    self._flush_logs_to_db(logs_to_flush)

                threading.Event().wait(5)  # 5초마다 플러시

            except Exception as e:
                logger.error(f"로그 플러시 루프 오류: {e}")
                threading.Event().wait(10)

    def _flush_logs_to_db(self, logs: List[LogEntry]):
        """로그를 데이터베이스에 플러시"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for log in logs:
                    conn.execute(
                        """
                        INSERT INTO plugin_logs 
                        (plugin_id, level, message, module, function, line_number, 
                         exception_info, context, trace_id, user_id, session_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            log.plugin_id,
                            log.level,
                            log.message,
                            log.module,
                            log.function,
                            log.line_number,
                            log.exception_info,
                            json.dumps(log.context),
                            log.trace_id,
                            log.user_id,
                            log.session_id,
                        ),
                    )

                conn.commit()

        except Exception as e:
            logger.error(f"로그 플러시 실패: {e}")

    def get_logger(self, plugin_id: str) -> PluginLogger:
        """플러그인 로거 가져오기"""
        if plugin_id not in self.loggers:
            self.loggers[plugin_id] = PluginLogger(plugin_id, self)
        return self.loggers[plugin_id]

    def add_log(self, log_entry: LogEntry):
        """로그 추가"""
        with self.queue_lock:
            self.log_queue.append(log_entry)

            # 큐 크기 제한
            if len(self.log_queue) > 1000:
                self.log_queue = self.log_queue[-500:]  # 최근 500개만 유지

    def get_logs(
        self,
        plugin_id: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[LogEntry]:
        """로그 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM plugin_logs WHERE 1=1"
                params = []

                if plugin_id:
                    query += " AND plugin_id = ?"
                    params.append(plugin_id)

                if level:
                    query += " AND level = ?"
                    params.append(level)

                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())

                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())

                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor = conn.execute(query, params)

                logs = []
                for row in cursor.fetchall():
                    logs.append(
                        LogEntry(
                            plugin_id=row["plugin_id"],
                            level=row["level"],
                            message=row["message"],
                            timestamp=datetime.fromisoformat(row["timestamp"]),
                            module=row["module"],
                            function=row["function"],
                            line_number=row["line_number"],
                            exception_info=row["exception_info"],
                            context=(
                                json.loads(row["context"]) if row["context"] else {}
                            ),
                            trace_id=row["trace_id"],
                            user_id=row["user_id"],
                            session_id=row["session_id"],
                        )
                    )

                return logs

        except Exception as e:
            logger.error(f"로그 조회 실패: {e}")
            return []

    def search_logs(
        self,
        search_term: str,
        plugin_id: Optional[str] = None,
        level: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> List[LogEntry]:
        """로그 검색"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM plugin_logs WHERE message LIKE ?"
                params = [f"%{search_term}%"]

                if plugin_id:
                    query += " AND plugin_id = ?"
                    params.append(plugin_id)

                if level:
                    query += " AND level = ?"
                    params.append(level)

                query += " ORDER BY timestamp DESC"

                cursor = conn.execute(query, params)

                logs = []
                for row in cursor.fetchall():
                    log_entry = LogEntry(
                        plugin_id=row["plugin_id"],
                        level=row["level"],
                        message=row["message"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        module=row["module"],
                        function=row["function"],
                        line_number=row["line_number"],
                        exception_info=row["exception_info"],
                        context=json.loads(row["context"]) if row["context"] else {},
                        trace_id=row["trace_id"],
                        user_id=row["user_id"],
                        session_id=row["session_id"],
                    )

                    # 대소문자 구분 검색
                    if (
                        case_sensitive
                        or search_term.lower() in log_entry.message.lower()
                    ):
                        logs.append(log_entry)

                return logs

        except Exception as e:
            logger.error(f"로그 검색 실패: {e}")
            return []

    def get_log_statistics(
        self, plugin_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Any]:
        """로그 통계 조회"""
        try:
            start_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # 기본 통계
                base_query = "SELECT COUNT(*) as total, level, COUNT(*) as count FROM plugin_logs WHERE timestamp >= ?"
                params = [start_date.isoformat()]

                if plugin_id:
                    base_query += " AND plugin_id = ?"
                    params.append(plugin_id)

                base_query += " GROUP BY level"

                cursor = conn.execute(base_query, params)

                level_stats = {}
                total_logs = 0

                for row in cursor.fetchall():
                    level_stats[row["level"]] = row["count"]
                    total_logs += row["count"]

                # 시간별 통계
                time_query = """
                    SELECT 
                        strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                        COUNT(*) as count
                    FROM plugin_logs 
                    WHERE timestamp >= ?
                """
                time_params = [start_date.isoformat()]

                if plugin_id:
                    time_query += " AND plugin_id = ?"
                    time_params.append(plugin_id)

                time_query += " GROUP BY hour ORDER BY hour"

                cursor = conn.execute(time_query, time_params)
                hourly_stats = {row["hour"]: row["count"] for row in cursor.fetchall()}

                # 플러그인별 통계
                plugin_query = """
                    SELECT plugin_id, COUNT(*) as count
                    FROM plugin_logs 
                    WHERE timestamp >= ?
                """
                plugin_params = [start_date.isoformat()]

                if plugin_id:
                    plugin_query += " AND plugin_id = ?"
                    plugin_params.append(plugin_id)

                plugin_query += " GROUP BY plugin_id ORDER BY count DESC"

                cursor = conn.execute(plugin_query, plugin_params)
                plugin_stats = {
                    row["plugin_id"]: row["count"] for row in cursor.fetchall()
                }

                return {
                    "total_logs": total_logs,
                    "level_distribution": level_stats,
                    "hourly_distribution": hourly_stats,
                    "plugin_distribution": plugin_stats,
                    "period_days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"로그 통계 조회 실패: {e}")
            return {}

    def add_log_pattern(self, pattern: str, description: str, severity: str = "INFO"):
        """로그 패턴 추가"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO log_patterns (pattern, description, severity)
                    VALUES (?, ?, ?)
                """,
                    (pattern, description, severity),
                )
                conn.commit()

            logger.info(f"로그 패턴 추가: {pattern}")

        except Exception as e:
            logger.error(f"로그 패턴 추가 실패: {e}")

    def analyze_log_patterns(
        self, plugin_id: Optional[str] = None, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """로그 패턴 분석"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)

            # 패턴 가져오기
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM log_patterns")
                patterns = [
                    (row["pattern"], row["description"], row["severity"])
                    for row in cursor.fetchall()
                ]

            # 로그에서 패턴 매칭
            logs = self.get_logs(
                plugin_id=plugin_id, start_time=start_time, limit=10000
            )

            pattern_matches = []
            for pattern, description, severity in patterns:
                matches = []
                for log in logs:
                    if re.search(pattern, log.message, re.IGNORECASE):
                        matches.append(log)

                if matches:
                    pattern_matches.append(
                        {
                            "pattern": pattern,
                            "description": description,
                            "severity": severity,
                            "match_count": len(matches),
                            "matches": matches[:10],  # 최대 10개만
                        }
                    )

            return pattern_matches

        except Exception as e:
            logger.error(f"로그 패턴 분석 실패: {e}")
            return []

    def cleanup_old_logs(self, days: int = 30):
        """오래된 로그 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                deleted_count = conn.execute(
                    """
                    DELETE FROM plugin_logs WHERE timestamp < ?
                """,
                    (cutoff_date.isoformat(),),
                ).rowcount
                conn.commit()

            logger.info(f"오래된 로그 {deleted_count}개 정리 완료")

        except Exception as e:
            logger.error(f"로그 정리 실패: {e}")

    def export_logs(
        self,
        output_path: str,
        plugin_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format: str = "json",
    ):
        """로그 내보내기"""
        try:
            logs = self.get_logs(
                plugin_id=plugin_id,
                start_time=start_time,
                end_time=end_time,
                limit=100000,
            )

            if format.lower() == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [
                            {
                                "plugin_id": log.plugin_id,
                                "level": log.level,
                                "message": log.message,
                                "timestamp": log.timestamp.isoformat(),
                                "module": log.module,
                                "function": log.function,
                                "line_number": log.line_number,
                                "exception_info": log.exception_info,
                                "context": log.context,
                                "trace_id": log.trace_id,
                                "user_id": log.user_id,
                                "session_id": log.session_id,
                            }
                            for log in logs
                        ],
                        f,
                        indent=2,
                        ensure_ascii=False,
                        default=str,
                    )

            elif format.lower() == "csv":
                import csv

                with open(output_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "timestamp",
                            "plugin_id",
                            "level",
                            "message",
                            "module",
                            "function",
                            "line_number",
                            "trace_id",
                        ]
                    )

                    for log in logs:
                        writer.writerow(
                            [
                                log.timestamp.isoformat(),
                                log.plugin_id,
                                log.level,
                                log.message,
                                log.module,
                                log.function,
                                log.line_number,
                                log.trace_id,
                            ]
                        )

            logger.info(f"로그 내보내기 완료: {output_path} ({len(logs)}개)")

        except Exception as e:
            logger.error(f"로그 내보내기 실패: {e}")

    def get_error_summary(
        self, plugin_id: Optional[str] = None, hours: int = 24
    ) -> Dict[str, Any]:
        """오류 요약 조회"""
        try:
            start_time = datetime.now() - timedelta(hours=hours)

            error_logs = self.get_logs(
                plugin_id=plugin_id, level="ERROR", start_time=start_time, limit=10000
            )

            # 오류 메시지별 그룹화
            error_groups = defaultdict(list)
            for log in error_logs:
                # 오류 메시지 정규화 (숫자나 경로 제거)
                normalized_message = re.sub(r"\d+", "N", log.message)
                normalized_message = re.sub(
                    r"[\\\/][^\\\/]+[\\\/]", "/path/", normalized_message
                )
                error_groups[normalized_message].append(log)

            # 상위 오류 정렬
            top_errors = sorted(
                error_groups.items(), key=lambda x: len(x[1]), reverse=True
            )[:10]

            return {
                "total_errors": len(error_logs),
                "unique_error_types": len(error_groups),
                "top_errors": [
                    {
                        "message": message,
                        "count": len(logs),
                        "examples": [log.message for log in logs[:3]],
                    }
                    for message, logs in top_errors
                ],
                "period_hours": hours,
            }

        except Exception as e:
            logger.error(f"오류 요약 조회 실패: {e}")
            return {}

    def shutdown(self):
        """로그 매니저 종료"""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5)

        # 남은 로그 플러시
        with self.queue_lock:
            if self.log_queue:
                self._flush_logs_to_db(self.log_queue)
                self.log_queue.clear()


# 컨텍스트 매니저로 로그 추적
@contextmanager
def log_trace_context(logger: PluginLogger, trace_id: str, **context):
    """로그 추적 컨텍스트"""
    original_trace_id = logger.trace_id
    original_context = logger.context.copy()

    try:
        logger.set_trace_id(trace_id)
        logger.set_context(**context)
        yield logger
    finally:
        logger.trace_id = original_trace_id
        logger.context = original_context


# 데코레이터로 로그 추적
def log_trace(trace_id: str):
    """로그 추적 데코레이터"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 플러그인 로거 찾기
            plugin_logger = None
            if args and hasattr(args[0], "logger"):
                plugin_logger = args[0].logger
            elif "logger" in kwargs:
                plugin_logger = kwargs["logger"]

            if plugin_logger:
                with log_trace_context(plugin_logger, trace_id):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


# CLI 인터페이스
def main():
    """CLI 메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="플러그인 로깅 시스템")
    parser.add_argument("--db-path", default="plugin_logs.db", help="데이터베이스 경로")
    parser.add_argument("--plugin-id", help="플러그인 ID")
    parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="로그 레벨",
    )
    parser.add_argument("--hours", type=int, default=24, help="조회 기간 (시간)")
    parser.add_argument("--limit", type=int, default=100, help="조회 개수 제한")
    parser.add_argument("--search", help="로그 검색어")
    parser.add_argument("--stats", action="store_true", help="로그 통계 조회")
    parser.add_argument("--errors", action="store_true", help="오류 요약 조회")
    parser.add_argument("--patterns", action="store_true", help="로그 패턴 분석")
    parser.add_argument("--export", metavar="OUTPUT_PATH", help="로그 내보내기")
    parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="내보내기 형식"
    )
    parser.add_argument(
        "--cleanup", type=int, metavar="DAYS", help="오래된 로그 정리 (일)"
    )

    args = parser.parse_args()

    log_manager = PluginLogManager(args.db_path)

    try:
        if args.stats:
            stats = log_manager.get_log_statistics(args.plugin_id, args.hours)
            print(f"\n=== 로그 통계 (최근 {args.hours}시간) ===")
            print(f"총 로그 수: {stats.get('total_logs', 0)}")
            print(f"레벨별 분포: {stats.get('level_distribution', {})}")
            print(
                f"플러그인별 분포: {dict(list(stats.get('plugin_distribution', {}).items())[:5])}"
            )

        elif args.errors:
            error_summary = log_manager.get_error_summary(args.plugin_id, args.hours)
            print(f"\n=== 오류 요약 (최근 {args.hours}시간) ===")
            print(f"총 오류 수: {error_summary.get('total_errors', 0)}")
            print(f"고유 오류 유형: {error_summary.get('unique_error_types', 0)}")
            print("\n상위 오류:")
            for error in error_summary.get("top_errors", [])[:5]:
                print(f"  {error['count']}회: {error['message'][:100]}...")

        elif args.patterns:
            patterns = log_manager.analyze_log_patterns(args.plugin_id, args.hours)
            print(f"\n=== 로그 패턴 분석 (최근 {args.hours}시간) ===")
            for pattern in patterns:
                print(f"패턴: {pattern['pattern']}")
                print(f"설명: {pattern['description']}")
                print(f"매칭 수: {pattern['match_count']}")
                print(f"심각도: {pattern['severity']}")
                print()

        elif args.export:
            start_time = datetime.now() - timedelta(hours=args.hours)
            log_manager.export_logs(
                args.export, args.plugin_id, start_time, format=args.format
            )
            print(f"로그가 {args.export}에 내보내졌습니다.")

        elif args.cleanup:
            log_manager.cleanup_old_logs(args.cleanup)
            print(f"{args.cleanup}일 이전 로그 정리 완료")

        elif args.search:
            logs = log_manager.search_logs(args.search, args.plugin_id, args.level)
            print(f"\n=== 로그 검색 결과 ({len(logs)}개) ===")
            for log in logs[: args.limit]:
                print(f"[{log.timestamp}] {log.level} - {log.plugin_id}: {log.message}")

        else:
            # 기본 로그 조회
            start_time = datetime.now() - timedelta(hours=args.hours)
            logs = log_manager.get_logs(
                args.plugin_id, args.level, start_time, limit=args.limit
            )

            print(f"\n=== 로그 조회 (최근 {args.hours}시간, {len(logs)}개) ===")
            for log in logs:
                print(f"[{log.timestamp}] {log.level} - {log.plugin_id}: {log.message}")
                if log.exception_info:
                    print(
                        f"  예외: {log.exception_info.split('Traceback')[-1].strip()}"
                    )

    finally:
        log_manager.shutdown()


if __name__ == "__main__":
    main()
