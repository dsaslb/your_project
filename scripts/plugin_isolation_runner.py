#!/usr/bin/env python3
"""
플러그인 격리 실행 환경
플러그인을 안전한 격리된 환경에서 실행하는 도구
"""

import json
import time
import shutil
import tempfile
import threading
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

import psutil


class PluginIsolationRunner:
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.running_plugins = {}
        self.isolation_config = {
            "max_memory_mb": 512,
            "max_cpu_percent": 50,
            "max_execution_time_seconds": 300,
            "max_file_size_mb": 10,
            "allowed_network_hosts": [],
            "read_only_filesystem": True,
            "disable_subprocess": True,
            "log_execution": True,
        }

    def create_isolation_environment(
        self, plugin_id: str, config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """격리 실행 환경 생성"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                return {"error": f"플러그인 {plugin_id}이 존재하지 않습니다."}

            # 설정 병합
            isolation_config = self.isolation_config.copy()
            if config:
                isolation_config.update(config)

            # 임시 격리 디렉토리 생성
            isolation_path = Path(
                tempfile.mkdtemp(prefix=f"plugin_isolated_{plugin_id}_")
            )

            # 플러그인 파일 복사
            isolated_plugin_path = isolation_path / plugin_id
            isolated_plugin_path.mkdir(exist_ok=True)

            # 필요한 파일만 복사
            allowed_files = [".py", ".json", ".txt", ".md"]
            for file_path in plugin_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in allowed_files:
                    relative_path = file_path.relative_to(plugin_path)
                    target_path = isolated_plugin_path / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(file_path, "rb") as src, open(target_path, "wb") as dst:
                        dst.write(src.read())

            # 격리 환경 설정 파일 생성
            isolation_env = {
                "plugin_id": plugin_id,
                "created_at": datetime.utcnow().isoformat(),
                "isolation_path": str(isolation_path),
                "plugin_path": str(isolated_plugin_path),
                "config": isolation_config,
                "status": "created",
            }

            env_config_path = isolation_path / "isolation_config.json"
            with open(env_config_path, "w", encoding="utf-8") as f:
                json.dump(isolation_env, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "isolation_path": str(isolation_path),
                "plugin_path": str(isolated_plugin_path),
                "config": isolation_config,
            }

        except Exception as e:
            return {"error": f"격리 환경 생성 중 오류: {e}"}

    def run_plugin_isolated(
        self,
        plugin_id: str,
        entry_point: str = "main.py",
        args: Optional[List[str]] = None,
        config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """플러그인을 격리된 환경에서 실행"""
        try:
            # 격리 환경 생성
            env_result = self.create_isolation_environment(plugin_id, config)
            if "error" in env_result:
                return env_result

            isolation_path = Path(env_result["isolation_path"])
            plugin_path = Path(env_result["plugin_path"])
            isolation_config = env_result["config"]

            # 실행 파일 경로
            entry_file = plugin_path / entry_point
            if not entry_file.exists():
                return {"error": f"진입점 파일이 존재하지 않습니다: {entry_point}"}

            # 실행 명령어 구성
            cmd = [sys.executable, str(entry_file)]
            if args:
                cmd.extend(args)

            # 실행 시작
            start_time = datetime.utcnow()
            process_id = f"{plugin_id}_{int(start_time.timestamp())}"

            # 프로세스 실행
            process = subprocess.Popen(
                cmd,
                cwd=str(plugin_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # 실행 정보 저장
            execution_info = {
                "process_id": process_id,
                "plugin_id": plugin_id,
                "process": process,
                "start_time": start_time,
                "isolation_path": str(isolation_path),
                "config": isolation_config,
                "status": "running",
                "output": {"stdout": [], "stderr": []},
                "resource_usage": [],
            }

            self.running_plugins[process_id] = execution_info

            # 모니터링 스레드 시작
            monitor_thread = threading.Thread(
                target=self._monitor_plugin_execution, args=(process_id,), daemon=True
            )
            monitor_thread.start()

            return {
                "success": True,
                "process_id": process_id,
                "plugin_id": plugin_id,
                "status": "started",
                "pid": process.pid,
            }

        except Exception as e:
            return {"error": f"플러그인 실행 중 오류: {e}"}

    def _monitor_plugin_execution(self, process_id: str):
        """플러그인 실행 모니터링"""
        try:
            execution_info = self.running_plugins[process_id]
            process = execution_info["process"]
            config = execution_info["config"]
            start_time = execution_info["start_time"]

            # 실행 시간 제한
            max_time = config["max_execution_time_seconds"]

            while process.poll() is None:
                # 실행 시간 체크
                elapsed_time = (datetime.utcnow() - start_time).total_seconds()
                if elapsed_time > max_time:
                    self._terminate_plugin(process_id, "실행 시간 초과")
                    break

                # 리소스 사용량 모니터링
                try:
                    process_info = psutil.Process(process.pid)
                    memory_mb = process_info.memory_info().rss / 1024 / 1024
                    cpu_percent = process_info.cpu_percent()

                    resource_usage = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "memory_mb": memory_mb,
                        "cpu_percent": cpu_percent,
                        "elapsed_time": elapsed_time,
                    }

                    execution_info["resource_usage"].append(resource_usage)

                    # 리소스 제한 체크
                    if memory_mb > config["max_memory_mb"]:
                        self._terminate_plugin(process_id, "메모리 사용량 초과")
                        break

                    if cpu_percent > config["max_cpu_percent"]:
                        self._terminate_plugin(process_id, "CPU 사용량 초과")
                        break

                except psutil.NoSuchProcess:
                    break

                time.sleep(1)

            # 실행 완료 처리
            self._finalize_plugin_execution(process_id)

        except Exception as e:
            print(f"모니터링 중 오류: {e}")
            self._terminate_plugin(process_id, f"모니터링 오류: {e}")

    def _terminate_plugin(self, process_id: str, reason: str):
        """플러그인 강제 종료"""
        try:
            execution_info = self.running_plugins[process_id]
            process = execution_info["process"]

            # 프로세스 종료
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            execution_info["status"] = "terminated"
            execution_info["termination_reason"] = reason

        except Exception as e:
            print(f"플러그인 종료 중 오류: {e}")

    def _finalize_plugin_execution(self, process_id: str):
        """플러그인 실행 완료 처리"""
        try:
            execution_info = self.running_plugins[process_id]
            process = execution_info["process"]

            # 출력 수집
            stdout, stderr = process.communicate()
            execution_info["output"]["stdout"] = stdout.splitlines() if stdout else []
            execution_info["output"]["stderr"] = stderr.splitlines() if stderr else []

            # 상태 업데이트
            if process.returncode == 0:
                execution_info["status"] = "completed"
            else:
                execution_info["status"] = "failed"
                execution_info["exit_code"] = process.returncode

            # 실행 로그 저장
            if execution_info["config"]["log_execution"]:
                self._save_execution_log(process_id, execution_info)

        except Exception as e:
            print(f"실행 완료 처리 중 오류: {e}")

    def _save_execution_log(self, process_id: str, execution_info: Dict[str, Any]):
        """실행 로그 저장"""
        try:
            log_data = {
                "process_id": process_id,
                "plugin_id": execution_info["plugin_id"],
                "start_time": execution_info["start_time"].isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "status": execution_info["status"],
                "exit_code": execution_info.get("exit_code"),
                "output": execution_info["output"],
                "resource_usage": execution_info["resource_usage"],
                "config": execution_info["config"],
            }

            # 로그 파일 저장
            log_path = Path("logs") / "plugin_execution"
            log_path.mkdir(parents=True, exist_ok=True)

            log_file = log_path / f"{process_id}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"로그 저장 중 오류: {e}")

    def get_plugin_status(self, process_id: str) -> Dict[str, Any]:
        """플러그인 실행 상태 조회"""
        try:
            if process_id not in self.running_plugins:
                return {"error": "실행 중인 플러그인이 아닙니다."}

            execution_info = self.running_plugins[process_id]
            process = execution_info["process"]

            status = {
                "process_id": process_id,
                "plugin_id": execution_info["plugin_id"],
                "status": execution_info["status"],
                "start_time": execution_info["start_time"].isoformat(),
                "elapsed_time": (
                    datetime.utcnow() - execution_info["start_time"]
                ).total_seconds(),
                "pid": process.pid,
                "is_alive": process.poll() is None,
            }

            # 리소스 사용량 (최근)
            if execution_info["resource_usage"]:
                latest_usage = execution_info["resource_usage"][-1]
                status["current_memory_mb"] = latest_usage["memory_mb"]
                status["current_cpu_percent"] = latest_usage["cpu_percent"]

            # 출력 (최근 10줄)
            if execution_info["output"]["stdout"]:
                status["recent_stdout"] = execution_info["output"]["stdout"][-10:]

            if execution_info["output"]["stderr"]:
                status["recent_stderr"] = execution_info["output"]["stderr"][-10:]

            return status

        except Exception as e:
            return {"error": f"상태 조회 중 오류: {e}"}

    def stop_plugin(self, process_id: str) -> Dict[str, Any]:
        """플러그인 실행 중지"""
        try:
            if process_id not in self.running_plugins:
                return {"error": "실행 중인 플러그인이 아닙니다."}

            self._terminate_plugin(process_id, "사용자 요청")

            return {"success": True, "process_id": process_id, "status": "stopped"}

        except Exception as e:
            return {"error": f"플러그인 중지 중 오류: {e}"}

    def list_running_plugins(self) -> List[Dict[str, Any]]:
        """실행 중인 플러그인 목록"""
        try:
            running_list = []

            for process_id, _ in self.running_plugins.items():
                status = self.get_plugin_status(process_id)
                if "error" not in status:
                    running_list.append(status)

            return running_list

        except Exception as e:
            return [{"error": f"목록 조회 중 오류: {e}"}]

    def cleanup_isolation_environment(self, process_id: str) -> Dict[str, Any]:
        """격리 환경 정리"""
        try:
            if process_id not in self.running_plugins:
                return {"error": "실행 중인 플러그인이 아닙니다."}

            execution_info = self.running_plugins[process_id]
            isolation_path = Path(execution_info["isolation_path"])

            # 프로세스가 완전히 종료될 때까지 대기
            process = execution_info["process"]
            if process.poll() is None:
                return {"error": "플러그인이 아직 실행 중입니다. 먼저 중지해주세요."}

            # 격리 디렉토리 삭제
            shutil.rmtree(isolation_path, ignore_errors=True)

            # 실행 정보 제거
            del self.running_plugins[process_id]

            return {
                "success": True,
                "process_id": process_id,
                "message": "격리 환경이 정리되었습니다.",
            }

        except Exception as e:
            return {"error": f"환경 정리 중 오류: {e}"}

    def get_execution_history(
        self, plugin_id: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """실행 히스토리 조회"""
        try:
            log_path = Path("logs") / "plugin_execution"
            if not log_path.exists():
                return []

            history = []

            # 로그 파일들 읽기
            for log_file in log_path.glob("*.json"):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        log_data = json.load(f)

                    # 플러그인 ID 필터링
                    if plugin_id and log_data.get("plugin_id") != plugin_id:
                        continue

                    history.append(log_data)

                except Exception:
                    continue

            # 시간순 정렬 (최신순)
            history.sort(key=lambda x: x.get("start_time", ""), reverse=True)

            return history[:limit]

        except Exception as e:
            return [{"error": f"히스토리 조회 중 오류: {e}"}]


def main():
    """메인 함수"""
    runner = PluginIsolationRunner()

    print("🔒 플러그인 격리 실행 환경")
    print("=" * 50)

    while True:
        print("\n사용 가능한 기능:")
        print("1. 플러그인 격리 실행")
        print("2. 실행 상태 조회")
        print("3. 플러그인 중지")
        print("4. 실행 중인 플러그인 목록")
        print("5. 격리 환경 정리")
        print("6. 실행 히스토리 조회")
        print("0. 종료")

        choice = input("\n선택 (0-6): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            plugin_id = input("플러그인 ID: ").strip()
            entry_point = input("진입점 파일 (기본값: main.py): ").strip() or "main.py"
            args_input = input("인수 (쉼표로 구분): ").strip()
            args = (
                [arg.strip() for arg in args_input.split(",") if arg.strip()]
                if args_input
                else None
            )

            # 격리 설정
            print("\n격리 설정 (Enter로 기본값 사용):")
            max_memory = input("최대 메모리 (MB, 기본값: 512): ").strip()
            max_cpu = input("최대 CPU (%) (기본값: 50): ").strip()
            max_time = input("최대 실행 시간 (초, 기본값: 300): ").strip()

            config = {}
            if max_memory:
                config["max_memory_mb"] = int(max_memory)
            if max_cpu:
                config["max_cpu_percent"] = int(max_cpu)
            if max_time:
                config["max_execution_time_seconds"] = int(max_time)

            result = runner.run_plugin_isolated(plugin_id, entry_point, args, config)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "2":
            process_id = input("프로세스 ID: ").strip()
            result = runner.get_plugin_status(process_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "3":
            process_id = input("프로세스 ID: ").strip()
            result = runner.stop_plugin(process_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "4":
            running_list = runner.list_running_plugins()
            if running_list:
                print(f"실행 중인 플러그인: {len(running_list)}개")
                for plugin in running_list:
                    print(
                        f"  - {plugin['plugin_id']} (PID: {plugin['process_id']}) - {plugin['status']}"
                    )
            else:
                print("실행 중인 플러그인이 없습니다.")
        elif choice == "5":
            process_id = input("프로세스 ID: ").strip()
            result = runner.cleanup_isolation_environment(process_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "6":
            plugin_id = input("플러그인 ID (Enter로 전체): ").strip() or None
            limit = input("조회 개수 (기본값: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10

            history = runner.get_execution_history(plugin_id, limit)
            if history:
                print(f"실행 히스토리: {len(history)}개")
                for entry in history:
                    print(
                        f"  - {entry['plugin_id']} ({entry['start_time']}) - {entry['status']}"
                    )
            else:
                print("실행 히스토리가 없습니다.")
        else:
            print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()
