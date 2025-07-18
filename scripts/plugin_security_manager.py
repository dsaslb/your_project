#!/usr/bin/env python3
"""
플러그인 보안 관리 시스템
플러그인의 보안을 강화하고 관리하는 도구
"""

import json
import hashlib
import hmac
import base64
import secrets
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import ast
import re


class PluginSecurityManager:
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.security_config = {
            "signature_algorithm": "sha256",
            "key_length": 32,
            "signature_expiry_days": 365,
            "max_file_size_mb": 50,
            "forbidden_imports": [
                "os",
                "subprocess",
                "sys",
                "eval",
                "exec",
                "open",
                "file",
                "input",
                "raw_input",
            ],
            "forbidden_functions": [
                "eval",
                "exec",
                "compile",
                "input",
                "raw_input",
                "open",
                "file",
                "__import__",
                "globals",
                "locals",
            ],
            "allowed_permissions": ["read", "write", "execute", "network", "database"],
        }

    def generate_security_key(self) -> str:
        """보안 키 생성"""
        return base64.b64encode(
            secrets.token_bytes(self.security_config["key_length"])
        ).decode()

    def sign_plugin(self, plugin_id: str, private_key: str) -> Dict[str, Any]:
        """플러그인 서명"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                return {"error": f"플러그인 {plugin_id}이 존재하지 않습니다."}

            # 플러그인 파일들의 해시 계산
            file_hashes = {}
            for file_path in plugin_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    with open(file_path, "rb") as f:
                        content = f.read()
                        file_hash = hashlib.sha256(content).hexdigest()
                        file_hashes[str(file_path.relative_to(plugin_path))] = file_hash

            # 메타데이터 생성
            metadata = {
                "plugin_id": plugin_id,
                "version": "1.0.0",
                "signed_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow()
                    + timedelta(days=self.security_config["signature_expiry_days"])
                ).isoformat(),
                "file_hashes": file_hashes,
                "signature_algorithm": self.security_config["signature_algorithm"],
            }

            # 서명 생성
            metadata_str = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
            signature = hmac.new(
                private_key.encode(), metadata_str.encode(), hashlib.sha256
            ).hexdigest()

            # 서명 파일 저장
            signature_data = {
                "metadata": metadata,
                "signature": signature,
                "public_key": self._derive_public_key(private_key),
            }

            signature_path = plugin_path / "config" / "plugin.sig"
            signature_path.parent.mkdir(exist_ok=True)

            with open(signature_path, "w", encoding="utf-8") as f:
                json.dump(signature_data, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "plugin_id": plugin_id,
                "signature": signature,
                "expires_at": metadata["expires_at"],
            }

        except Exception as e:
            return {"error": f"서명 생성 중 오류: {e}"}

    def verify_plugin_signature(
        self, plugin_id: str, public_key: str
    ) -> Dict[str, Any]:
        """플러그인 서명 검증"""
        try:
            plugin_path = self.base_path / plugin_id
            signature_path = plugin_path / "config" / "plugin.sig"

            if not signature_path.exists():
                return {"error": "서명 파일이 존재하지 않습니다."}

            # 서명 파일 읽기
            with open(signature_path, "r", encoding="utf-8") as f:
                signature_data = json.load(f)

            metadata = signature_data["metadata"]
            stored_signature = signature_data["signature"]
            stored_public_key = signature_data["public_key"]

            # 만료일 검사
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            if datetime.utcnow() > expires_at:
                return {"error": "서명이 만료되었습니다."}

            # 공개키 검증
            if stored_public_key != public_key:
                return {"error": "공개키가 일치하지 않습니다."}

            # 파일 해시 검증
            for file_path, expected_hash in metadata["file_hashes"].items():
                full_path = plugin_path / file_path
                if not full_path.exists():
                    return {"error": f"파일이 존재하지 않습니다: {file_path}"}

                with open(full_path, "rb") as f:
                    content = f.read()
                    actual_hash = hashlib.sha256(content).hexdigest()

                    if actual_hash != expected_hash:
                        return {"error": f"파일 해시가 일치하지 않습니다: {file_path}"}

            # 서명 검증
            metadata_str = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
            expected_signature = hmac.new(
                public_key.encode(), metadata_str.encode(), hashlib.sha256
            ).hexdigest()

            if stored_signature != expected_signature:
                return {"error": "서명이 유효하지 않습니다."}

            return {
                "success": True,
                "plugin_id": plugin_id,
                "verified_at": datetime.utcnow().isoformat(),
                "expires_at": metadata["expires_at"],
            }

        except Exception as e:
            return {"error": f"서명 검증 중 오류: {e}"}

    def _derive_public_key(self, private_key: str) -> str:
        """개인키로부터 공개키 유도"""
        return hashlib.sha256(private_key.encode()).hexdigest()

    def scan_plugin_security(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인 보안 스캔"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                return {"error": f"플러그인 {plugin_id}이 존재하지 않습니다."}

            scan_results = {
                "plugin_id": plugin_id,
                "scanned_at": datetime.utcnow().isoformat(),
                "vulnerabilities": [],
                "warnings": [],
                "security_score": 100,
                "file_analysis": {},
            }

            # Python 파일 보안 분석
            for py_file in plugin_path.rglob("*.py"):
                file_analysis = self._analyze_python_file(py_file)
                scan_results["file_analysis"][
                    str(py_file.relative_to(plugin_path))
                ] = file_analysis

                # 취약점 점수 계산
                if file_analysis["vulnerabilities"]:
                    scan_results["vulnerabilities"].extend(
                        file_analysis["vulnerabilities"]
                    )
                    scan_results["security_score"] -= (
                        len(file_analysis["vulnerabilities"]) * 10
                    )

                if file_analysis["warnings"]:
                    scan_results["warnings"].extend(file_analysis["warnings"])
                    scan_results["security_score"] -= len(file_analysis["warnings"]) * 5

            # 최소 보안 점수 보장
            scan_results["security_score"] = max(0, scan_results["security_score"])

            # 전체 보안 평가
            if scan_results["security_score"] >= 80:
                scan_results["security_level"] = "high"
            elif scan_results["security_score"] >= 60:
                scan_results["security_level"] = "medium"
            else:
                scan_results["security_level"] = "low"

            return scan_results

        except Exception as e:
            return {"error": f"보안 스캔 중 오류: {e}"}

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Python 파일 보안 분석"""
        analysis = {
            "vulnerabilities": [],
            "warnings": [],
            "imports": [],
            "functions": [],
            "file_size": 0,
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                analysis["file_size"] = len(content)

            # AST 분석
            try:
                tree = ast.parse(content)
                analysis.update(self._analyze_ast(tree))
            except SyntaxError as e:
                analysis["vulnerabilities"].append(f"구문 오류: {e}")

            # 정규식 기반 추가 검사
            analysis.update(self._regex_security_check(content))

        except Exception as e:
            analysis["vulnerabilities"].append(f"파일 분석 오류: {e}")

        return analysis

    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """AST 기반 보안 분석"""
        analysis = {
            "imports": [],
            "functions": [],
            "vulnerabilities": [],
            "warnings": [],
        }

        for node in ast.walk(tree):
            # import 문 분석
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append(alias.name)
                    if alias.name in self.security_config["forbidden_imports"]:
                        analysis["vulnerabilities"].append(
                            f"금지된 import: {alias.name}"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module in self.security_config["forbidden_imports"]:
                    analysis["vulnerabilities"].append(f"금지된 import: {node.module}")
                analysis["imports"].append(node.module or "")

            # 함수 호출 분석
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    analysis["functions"].append(func_name)
                    if func_name in self.security_config["forbidden_functions"]:
                        analysis["vulnerabilities"].append(
                            f"금지된 함수 호출: {func_name}"
                        )

            # eval/exec 사용 검사
            elif isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id in ["eval", "exec"]:
                            analysis["vulnerabilities"].append(
                                f"위험한 함수 사용: {node.value.func.id}"
                            )

        return analysis

    def _regex_security_check(self, content: str) -> Dict[str, Any]:
        """정규식 기반 보안 검사"""
        analysis = {"vulnerabilities": [], "warnings": []}

        # 위험한 패턴 검사
        dangerous_patterns = [
            (r"eval\s*\(", "eval 함수 사용"),
            (r"exec\s*\(", "exec 함수 사용"),
            (r"__import__\s*\(", "__import__ 함수 사용"),
            (r"globals\s*\(", "globals 함수 사용"),
            (r"locals\s*\(", "locals 함수 사용"),
            (r"input\s*\(", "input 함수 사용"),
            (r"raw_input\s*\(", "raw_input 함수 사용"),
            (r"open\s*\([^)]*w[^)]*\)", "파일 쓰기 작업"),
            (r"subprocess\s*\.", "subprocess 모듈 사용"),
            (r"os\s*\.", "os 모듈 사용"),
            (r"sys\s*\.", "sys 모듈 사용"),
        ]

        for pattern, description in dangerous_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis["warnings"].append(f"{description} ({len(matches)}회)")

        return analysis

    def create_sandbox_environment(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인 샌드박스 환경 생성"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                return {"error": f"플러그인 {plugin_id}이 존재하지 않습니다."}

            # 임시 샌드박스 디렉토리 생성
            sandbox_path = Path(tempfile.mkdtemp(prefix=f"plugin_sandbox_{plugin_id}_"))

            # 플러그인 파일 복사 (읽기 전용)
            sandbox_plugin_path = sandbox_path / plugin_id
            sandbox_plugin_path.mkdir(exist_ok=True)

            # 필요한 파일만 복사
            allowed_extensions = [".py", ".json", ".txt", ".md"]
            for file_path in plugin_path.rglob("*"):
                if file_path.is_file():
                    if file_path.suffix in allowed_extensions:
                        relative_path = file_path.relative_to(plugin_path)
                        target_path = sandbox_plugin_path / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # 파일 복사 (읽기 전용)
                        with open(file_path, "rb") as src, open(
                            target_path, "wb"
                        ) as dst:
                            dst.write(src.read())

                        # 읽기 전용 권한 설정
                        target_path.chmod(0o444)

            # 샌드박스 설정 파일 생성
            sandbox_config = {
                "plugin_id": plugin_id,
                "created_at": datetime.utcnow().isoformat(),
                "sandbox_path": str(sandbox_path),
                "restrictions": {
                    "read_only": True,
                    "no_network": True,
                    "no_file_write": True,
                    "no_subprocess": True,
                    "memory_limit_mb": 100,
                    "cpu_limit_percent": 50,
                },
            }

            config_path = sandbox_path / "sandbox_config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sandbox_config, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "sandbox_path": str(sandbox_path),
                "plugin_path": str(sandbox_plugin_path),
                "config": sandbox_config,
            }

        except Exception as e:
            return {"error": f"샌드박스 생성 중 오류: {e}"}

    def manage_plugin_permissions(
        self, plugin_id: str, permissions: List[str]
    ) -> Dict[str, Any]:
        """플러그인 권한 관리"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                return {"error": f"플러그인 {plugin_id}이 존재하지 않습니다."}

            # 권한 검증
            invalid_permissions = [
                p
                for p in permissions
                if p not in self.security_config["allowed_permissions"]
            ]
            if invalid_permissions:
                return {"error": f"유효하지 않은 권한: {invalid_permissions}"}

            # 권한 설정 파일 생성/업데이트
            permissions_config = {
                "plugin_id": plugin_id,
                "permissions": permissions,
                "updated_at": datetime.utcnow().isoformat(),
                "granted_by": "security_manager",
            }

            config_path = plugin_path / "config" / "permissions.json"
            config_path.parent.mkdir(exist_ok=True)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(permissions_config, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "plugin_id": plugin_id,
                "permissions": permissions,
                "updated_at": permissions_config["updated_at"],
            }

        except Exception as e:
            return {"error": f"권한 관리 중 오류: {e}"}

    def get_plugin_permissions(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인 권한 조회"""
        try:
            plugin_path = self.base_path / plugin_id
            permissions_path = plugin_path / "config" / "permissions.json"

            if not permissions_path.exists():
                return {
                    "plugin_id": plugin_id,
                    "permissions": [],
                    "message": "권한 설정이 없습니다.",
                }

            with open(permissions_path, "r", encoding="utf-8") as f:
                permissions_config = json.load(f)

            return permissions_config

        except Exception as e:
            return {"error": f"권한 조회 중 오류: {e}"}

    def generate_security_report(self, plugin_id: str) -> str:
        """보안 리포트 생성"""
        try:
            # 보안 스캔 실행
            scan_results = self.scan_plugin_security(plugin_id)
            if "error" in scan_results:
                return f"보안 스캔 실패: {scan_results['error']}"

            # 권한 정보 조회
            permissions = self.get_plugin_permissions(plugin_id)

            # 서명 정보 확인
            plugin_path = self.base_path / plugin_id
            signature_path = plugin_path / "config" / "plugin.sig"
            has_signature = signature_path.exists()

            # 리포트 생성
            report = {
                "plugin_id": plugin_id,
                "generated_at": datetime.utcnow().isoformat(),
                "security_scan": scan_results,
                "permissions": permissions,
                "signature": {"has_signature": has_signature, "verified": False},
                "recommendations": [],
            }

            # 권장사항 생성
            if scan_results["security_score"] < 80:
                report["recommendations"].append(
                    "보안 점수가 낮습니다. 취약점을 수정하세요."
                )

            if not has_signature:
                report["recommendations"].append("플러그인 서명이 필요합니다.")

            if not permissions.get("permissions"):
                report["recommendations"].append("권한 설정이 필요합니다.")

            # 리포트 파일 저장
            report_path = plugin_path / "security_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            return str(report_path)

        except Exception as e:
            return f"보안 리포트 생성 중 오류: {e}"


def main():
    """메인 함수"""
    security_manager = PluginSecurityManager()

    print("🔒 플러그인 보안 관리 시스템")
    print("=" * 50)

    while True:
        print("\n사용 가능한 기능:")
        print("1. 플러그인 서명")
        print("2. 서명 검증")
        print("3. 보안 스캔")
        print("4. 샌드박스 환경 생성")
        print("5. 권한 관리")
        print("6. 권한 조회")
        print("7. 보안 리포트 생성")
        print("8. 보안 키 생성")
        print("0. 종료")

        choice = input("\n선택 (0-8): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            plugin_id = input("플러그인 ID: ").strip()
            private_key = input("개인키 (Enter로 자동 생성): ").strip()
            if not private_key:
                private_key = security_manager.generate_security_key()
                print(f"생성된 개인키: {private_key}")

            result = security_manager.sign_plugin(plugin_id, private_key)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "2":
            plugin_id = input("플러그인 ID: ").strip()
            public_key = input("공개키: ").strip()
            result = security_manager.verify_plugin_signature(plugin_id, public_key)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "3":
            plugin_id = input("플러그인 ID: ").strip()
            result = security_manager.scan_plugin_security(plugin_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "4":
            plugin_id = input("플러그인 ID: ").strip()
            result = security_manager.create_sandbox_environment(plugin_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "5":
            plugin_id = input("플러그인 ID: ").strip()
            print("권한 목록: read, write, execute, network, database")
            permissions_input = input("권한 (쉼표로 구분): ").strip()
            permissions = [p.strip() for p in permissions_input.split(",") if p.strip()]
            result = security_manager.manage_plugin_permissions(plugin_id, permissions)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "6":
            plugin_id = input("플러그인 ID: ").strip()
            result = security_manager.get_plugin_permissions(plugin_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "7":
            plugin_id = input("플러그인 ID: ").strip()
            report_path = security_manager.generate_security_report(plugin_id)
            print(f"보안 리포트 생성 완료: {report_path}")
        elif choice == "8":
            key = security_manager.generate_security_key()
            print(f"생성된 보안 키: {key}")
        else:
            print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()
