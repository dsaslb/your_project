import shutil
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class PluginReleaseManager:
    """플러그인 배포/업데이트/롤백 기록 및 파일 관리"""
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)

    def get_release_dir(self, plugin_name: str) -> Path:
        return self.plugins_dir / plugin_name / "releases"

    def list_releases(self, plugin_name: str) -> List[Dict]:
        """플러그인 배포본(버전) 목록 조회"""
        release_dir = self.get_release_dir(plugin_name)
        if not release_dir.exists():
            return []
        releases = []
        for item in sorted(release_dir.iterdir(), reverse=True):
            if item.is_dir():
                manifest = item / "plugin.json"
                if manifest.exists():
                    with open(manifest, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    releases.append({
                        "version": item.name,
                        "manifest": config,
                        "path": str(item)
                    })
        return releases

    def save_release(self, plugin_name: str, version: str, plugin_dir: Optional[Path] = None) -> bool:
        """플러그인 현재 상태를 releases/{version}에 저장"""
        try:
            src_dir = plugin_dir or (self.plugins_dir / plugin_name)
            release_dir = self.get_release_dir(plugin_name) / version
            if release_dir.exists():
                shutil.rmtree(release_dir)
            shutil.copytree(src_dir, release_dir, dirs_exist_ok=True)
            return True
        except Exception as e:
            print(f"플러그인 배포본 저장 실패: {e}")
            return False

    def rollback_release(self, plugin_name: str, version: str) -> bool:
        """지정 버전으로 롤백 (releases/{version} → plugins/{plugin_name})"""
        try:
            release_dir = self.get_release_dir(plugin_name) / version
            plugin_dir = self.plugins_dir / plugin_name
            if not release_dir.exists():
                print(f"롤백 대상 버전이 존재하지 않음: {release_dir}")
                return False
            # 기존 플러그인 백업
            backup_dir = self.plugins_dir / f"{plugin_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if plugin_dir.exists():
                shutil.copytree(plugin_dir, backup_dir)
                shutil.rmtree(plugin_dir)
            shutil.copytree(release_dir, plugin_dir)
            return True
        except Exception as e:
            print(f"롤백 실패: {e}")
            return False

    def log_release_action(self, plugin_name: str, action: str, version: str, user: str = "system", detail: str = ""):
        """배포/업데이트/롤백 이력 기록"""
        log_file = self.plugins_dir / plugin_name / "release_history.json"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "version": version,
            "user": user,
            "detail": detail
        }
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(entry)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def get_release_history(self, plugin_name: str, limit: int = 50) -> List[Dict]:
        log_file = self.plugins_dir / plugin_name / "release_history.json"
        if not log_file.exists():
            return []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return logs[-limit:]
        except Exception:
            return [] 