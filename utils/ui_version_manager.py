"""
UI 버전 관리 시스템
UI/UX 변경 시 안전하게 버전을 관리하고 롤백할 수 있도록 도와주는 시스템
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class UIVersionManager:
    """UI 버전 관리 클래스"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "ui_backups"
        self.version_file = self.project_root / "ui_version.json"
        self.backup_dir.mkdir(exist_ok=True)
        self.ui_dirs = ["templates", "static/css", "static/js", "static/images"]
        self.load_version_info()

    def load_version_info(self):
        if self.version_file.exists():
            with open(self.version_file, "r", encoding="utf-8") as f:
                self.version_info = json.load(f)
        else:
            self.version_info = {
                "current_version": None,
                "versions": [],
                "last_backup": None,
            }
            self.save_version_info()

    def save_version_info(self):
        with open(self.version_file, "w", encoding="utf-8") as f:
            json.dump(self.version_info, f, indent=2, ensure_ascii=False)

    def create_backup(self, version_name: str, description: str = "") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{version_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        for ui_dir in self.ui_dirs:
            src = self.project_root / ui_dir
            dst = backup_path / ui_dir
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        version_data = {
            "version": version_name,
            "timestamp": timestamp,
            "description": description,
            "backup_path": str(backup_path),
        }
        self.version_info["versions"].append(version_data)
        self.version_info["current_version"] = version_name
        self.version_info["last_backup"] = timestamp
        self.save_version_info()
        logger.info(f"UI 백업 생성 완료: {backup_name}")
        return backup_name

    def restore_backup(self, version_name: str) -> bool:
        version_data = next(
            (v for v in self.version_info["versions"] if v["version"] == version_name),
            None,
        )
        if not version_data:
            logger.error(f"버전 {version_name}을 찾을 수 없습니다.")
            return False
        backup_path = Path(version_data["backup_path"])
        if not backup_path.exists():
            logger.error(f"백업 경로가 존재하지 않습니다: {backup_path}")
            return False
        # 현재 상태 백업(안전장치)
        self.create_backup("pre_restore", f"복원 전 백업 - {version_name} 복원용")
        for ui_dir in self.ui_dirs:
            src = backup_path / ui_dir
            dst = self.project_root / ui_dir
            if src.exists():
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        self.version_info["current_version"] = version_name
        self.save_version_info()
        logger.info(f"UI 복원 완료: {version_name}")
        return True

    def list_versions(self) -> List[Dict]:
        return self.version_info["versions"]

    def get_current_version(self) -> Optional[str]:
        return self.version_info["current_version"]

    def compare_versions(self, version1: str, version2: str) -> Dict:
        v1 = next(
            (v for v in self.version_info["versions"] if v["version"] == version1), None
        )
        v2 = next(
            (v for v in self.version_info["versions"] if v["version"] == version2), None
        )
        if not v1 or not v2:
            return {"error": "버전을 찾을 수 없습니다."}
        v1_files = set(self._get_file_list_from_backup(v1["backup_path"]))
        v2_files = set(self._get_file_list_from_backup(v2["backup_path"]))
        return {
            "added": list(v2_files - v1_files),
            "removed": list(v1_files - v2_files),
            "common": list(v1_files & v2_files),
        }

    def _get_file_list_from_backup(self, backup_path: str) -> List[str]:
        files = []
        backup_path = Path(backup_path)
        for ui_dir in self.ui_dirs:
            dir_path = backup_path / ui_dir
            if dir_path.exists():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        files.append(str(file_path.relative_to(backup_path)))
        return files


# 전역 인스턴스
ui_manager = UIVersionManager()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UI 버전 관리 자동화 도구")
    parser.add_argument(
        "action", choices=["backup", "restore", "list", "compare"], help="실행할 작업"
    )
    parser.add_argument("--version", help="백업/복원/비교할 버전명")
    parser.add_argument("--version2", help="비교할 두 번째 버전명")
    parser.add_argument("--desc", help="백업 설명")
    args = parser.parse_args()

    if args.action == "backup":
        name = args.version or input("백업 버전명을 입력하세요: ")
        desc = args.desc or ""
        result = ui_manager.create_backup(name, desc)
        print(f"백업 완료: {result}")
    elif args.action == "restore":
        name = args.version or input("복원할 버전명을 입력하세요: ")
        ok = ui_manager.restore_backup(name)
        print("복원 성공" if ok else "복원 실패")
    elif args.action == "list":
        for v in ui_manager.list_versions():
            print(
                f"버전: {v['version']}, 날짜: {v['timestamp']}, 설명: {v.get('description','')}"
            )
    elif args.action == "compare":
        v1 = args.version or input("비교할 첫 번째 버전명: ")
        v2 = args.version2 or input("비교할 두 번째 버전명: ")
        diff = ui_manager.compare_versions(v1, v2)
        print(json.dumps(diff, indent=2, ensure_ascii=False))
