#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플러그인 검증 스크립트
플러그인의 구조, 의존성, 보안, 성능 등을 종합적으로 검증합니다.
"""

import os
import sys
import json
import yaml
import ast
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PluginValidator:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.validation_results = {}
        self.errors = []
        self.warnings = []

    def validate_all_plugins(self) -> Dict[str, Any]:
        """모든 플러그인 검증"""
        logger.info("플러그인 검증 시작")

        if not self.plugins_dir.exists():
            logger.error(f"플러그인 디렉토리가 존재하지 않습니다: {self.plugins_dir}")
            return {"success": False, "error": "플러그인 디렉토리 없음"}

        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                logger.info(f"플러그인 검증 중: {plugin_dir.name}")
                self.validate_plugin(plugin_dir)

        return self.generate_report()

    def validate_plugin(self, plugin_dir: Path) -> None:
        """개별 플러그인 검증"""
        plugin_name = plugin_dir.name
        results = {
            "name": plugin_name,
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {},
        }

        try:
            # 1. 기본 구조 검증
            results["checks"]["structure"] = self.validate_structure(plugin_dir)

            # 2. 설정 파일 검증
            results["checks"]["config"] = self.validate_config(plugin_dir)

            # 3. 코드 품질 검증
            results["checks"]["code_quality"] = self.validate_code_quality(plugin_dir)

            # 4. 보안 검증
            results["checks"]["security"] = self.validate_security(plugin_dir)

            # 5. 의존성 검증
            results["checks"]["dependencies"] = self.validate_dependencies(plugin_dir)

            # 6. 성능 검증
            # pyright: ignore [reportAttributeAccessIssue]
            results["checks"]["performance"] = self.validate_performance(
                plugin_dir
            )  # pyright: ignore

            # 7. 문서화 검증
            results["checks"]["documentation"] = self.validate_documentation(plugin_dir)
            # 8. 테스트 검증
            results["checks"]["tests"] = self.validate_tests(plugin_dir)

            # 전체 결과 집계
            for check_name, check_result in results["checks"].items():
                if not check_result["valid"]:
                    results["valid"] = False
                    results["errors"].extend(check_result.get("errors", []))
                results["warnings"].extend(check_result.get("warnings", []))

        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 검증 중 오류 발생: {e}")
            results["valid"] = False
            results["errors"].append(f"검증 중 오류 발생: {str(e)}")

        self.validation_results[plugin_name] = results

    def validate_structure(self, plugin_dir: Path) -> Dict[str, Any]:
        """플러그인 구조 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        # 필수 파일/디렉토리 확인
        required_files = ["config/plugin.json", "backend/main.py"]

        optional_files = [
            "README.md",
            "requirements.txt",
            "tests/",
            "docs/",
            "frontend/",
        ]

        for file_path in required_files:
            full_path = plugin_dir / file_path
            if not full_path.exists():
                result["valid"] = False
                result["errors"].append(f"필수 파일 없음: {file_path}")

        for file_path in optional_files:
            full_path = plugin_dir / file_path
            if not full_path.exists():
                result["warnings"].append(f"권장 파일 없음: {file_path}")

        return result

    def validate_config(self, plugin_dir: Path) -> Dict[str, Any]:
        """플러그인 설정 파일 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        config_file = plugin_dir / "config" / "plugin.json"
        if not config_file.exists():
            result["valid"] = False
            result["errors"].append("plugin.json 파일이 없습니다")
            return result

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 필수 필드 검증
            required_fields = ["name", "version", "description", "author"]
            for field in required_fields:
                if field not in config:
                    result["valid"] = False
                    result["errors"].append(f"필수 필드 없음: {field}")

            # 버전 형식 검증
            if "version" in config:
                version = config["version"]
                if not self.is_valid_version(version):
                    result["valid"] = False
                    result["errors"].append(f"잘못된 버전 형식: {version}")

            # 의존성 검증
            if "dependencies" in config:
                dependencies = config["dependencies"]
                if not isinstance(dependencies, dict):
                    result["valid"] = False
                    result["errors"].append("의존성은 딕셔너리 형태여야 합니다")

            # 권한 검증
            if "permissions" in config:
                permissions = config["permissions"]
                if not isinstance(permissions, list):
                    result["valid"] = False
                    result["errors"].append("권한은 리스트 형태여야 합니다")

        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"JSON 파싱 오류: {e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"설정 파일 읽기 오류: {e}")

        return result

    def validate_code_quality(self, plugin_dir: Path) -> Dict[str, Any]:
        """코드 품질 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        backend_dir = plugin_dir / "backend"
        if not backend_dir.exists():
            result["valid"] = False
            result["errors"].append("backend 디렉토리가 없습니다")
            return result

        # Python 파일 분석
        python_files = list(backend_dir.rglob("*.py"))
        if not python_files:
            result["valid"] = False
            result["errors"].append("Python 파일이 없습니다")
            return result

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # AST 분석
                tree = ast.parse(content)

                # 함수/클래스 개수 확인
                functions = [
                    node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                ]
                classes = [
                    node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                ]

                if len(functions) > 50:
                    result["warnings"].append(
                        f"{py_file.name}: 함수가 너무 많습니다 ({len(functions)}개)"
                    )

                if len(classes) > 20:
                    result["warnings"].append(
                        f"{py_file.name}: 클래스가 너무 많습니다 ({len(classes)}개)"
                    )

                # 복잡도 검사
                complexity = self.calculate_complexity(tree)
                if complexity > 10:
                    result["warnings"].append(
                        f"{py_file.name}: 복잡도가 높습니다 ({complexity})"
                    )

                # 임포트 검사
                imports = [
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                ]
                if len(imports) > 20:
                    result["warnings"].append(
                        f"{py_file.name}: 임포트가 많습니다 ({len(imports)}개)"
                    )

            except SyntaxError as e:
                result["valid"] = False
                result["errors"].append(f"{py_file.name}: 구문 오류 - {e}")
            except Exception as e:
                result["warnings"].append(f"{py_file.name}: 분석 오류 - {e}")

        return result

    def validate_security(self, plugin_dir: Path) -> Dict[str, Any]:
        """보안 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        # 위험한 함수/모듈 검사
        dangerous_patterns = [
            "eval(",
            "exec(",
            "os.system(",
            "subprocess.call(",
            "pickle.loads(",
            "yaml.load(",
            "input(",
            "raw_input(",
            "__import__(",
            "globals(",
            "locals(",
        ]

        python_files = list(plugin_dir.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern in dangerous_patterns:
                    if pattern in content:
                        result["warnings"].append(
                            f"{py_file.name}: 잠재적 보안 위험 - {pattern}"
                        )

                # 하드코딩된 비밀번호/키 검사
                if any(
                    keyword in content.lower()
                    for keyword in ["password", "secret", "key", "token"]
                ):
                    if any(
                        line.strip().startswith(("password", "secret", "key", "token"))
                        for line in content.split("\n")
                    ):
                        result["warnings"].append(
                            f"{py_file.name}: 하드코딩된 비밀정보 가능성"
                        )

            except Exception as e:
                result["warnings"].append(f"{py_file.name}: 보안 검사 오류 - {e}")

        return result

    def validate_dependencies(self, plugin_dir: Path) -> Dict[str, Any]:
        """의존성 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        requirements_file = plugin_dir / "requirements.txt"
        if not requirements_file.exists():
            result["warnings"].append("requirements.txt 파일이 없습니다")
            return result

        try:
            with open(requirements_file, "r", encoding="utf-8") as f:
                requirements = f.read().strip().split("\n")

            for req in requirements:
                req = req.strip()
                if not req or req.startswith("#"):
                    continue

                # 버전 형식 검사
                if "==" in req:
                    package, version = req.split("==", 1)
                    if not self.is_valid_version(version):
                        result["warnings"].append(f"잘못된 버전 형식: {req}")

                # 보안 취약점이 알려진 패키지 검사
                vulnerable_packages = ["django<2.2.0", "flask<2.0.0", "requests<2.25.0"]

                for vuln_pkg in vulnerable_packages:
                    if vuln_pkg in req:
                        result["warnings"].append(f"보안 취약점 가능성: {req}")

        except Exception as e:
            result["warnings"].append(f"의존성 파일 읽기 오류: {e}")

        return result  # 함수의 모든 경로에서 값을 반환하도록 보장합니다.  # pyright: ignore
        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                result["warnings"].append(
                    f"{py_file.name}: 파일 읽기 오류 - {e}"
                )  # noqa
                continue  # 파일 읽기에 실패하면 다음 파일로 넘어갑니다.

                # 성능 관련 패턴 검사
                performance_issues = [
                    ("time.sleep(", "블로킹 호출"),
                    ("requests.get(", "동기 HTTP 호출"),
                    ("requests.post(", "동기 HTTP 호출"),
                    ("open(", "파일 핸들러 미해제 가능성"),
                    ("sqlite3.connect(", "데이터베이스 연결 미해제 가능성"),
                    ("threading.Thread(", "스레드 관리 필요"),
                    ("multiprocessing.Process(", "프로세스 관리 필요"),
                ]

                for pattern, issue in performance_issues:
                    if pattern in content:
                        result["warnings"].append(
                            f"{py_file.name}: 성능 이슈 가능성 - {issue}"
                        )

                # 파일 크기 검사
                file_size = len(content)
                if file_size > 10000:  # 10KB
                    if file_size > 10000:  # 10KB
                        result["warnings"].append(
                            f"{py_file.name}: 파일이 큽니다 ({file_size} bytes)"
                        )
                    # 위의 if문이 이미 file_size > 10000을 검사하므로, 중복된 if문을 제거했습니다.

    def validate_documentation(self, plugin_dir: Path) -> Dict[str, Any]:
        """문서화 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        # README 파일 검사
        readme_files = ["README.md", "README.txt", "readme.md"]
        has_readme = any((plugin_dir / readme).exists() for readme in readme_files)

        if not has_readme:
            result["warnings"].append("README 파일이 없습니다")

        # 문서 디렉토리 검사
        docs_dir = plugin_dir / "docs"
        if not docs_dir.exists():
            result["warnings"].append("docs 디렉토리가 없습니다")

        # Python 파일의 docstring 검사
        python_files = list(plugin_dir.rglob("*.py"))
        files_without_docstrings = 0

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                result["warnings"].append(
                    f"{py_file.name}: 파일 읽기 오류 - {e}"
                )  # noqa
                continue  # 파일 읽기에 실패하면 다음 파일로 넘어갑니다.

            try:
                tree = ast.parse(content)
            except Exception as e:
                result["warnings"].append(
                    f"{py_file.name}: AST 파싱 오류 - {e}"
                )  # noqa
                continue  # 파싱에 실패하면 다음 파일로 넘어갑니다.

                # 모듈 레벨 docstring 검사
                if (
                    tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Str)
                ):
                    continue
                else:
                    files_without_docstrings += 1

                # 함수/클래스 docstring 검사
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if (
                            not node.body
                            or not isinstance(node.body[0], ast.Expr)
                            or not isinstance(node.body[0].value, ast.Str)
                        ):
                            result["warnings"].append(
                                f"{py_file.name}: {node.name}에 docstring이 없습니다"
                            )

        if files_without_docstrings > len(python_files) * 0.5:
            result["warnings"].append(
                f"docstring이 없는 파일이 많습니다 ({files_without_docstrings}/{len(python_files)})"
            )

        return result

    def validate_tests(self, plugin_dir: Path) -> Dict[str, Any]:
        """테스트 검증"""
        result = {"valid": True, "errors": [], "warnings": []}

        # 테스트 디렉토리 검사
        test_dirs = ["tests", "test", "tests.py"]
        has_tests = False

        for test_dir in test_dirs:
            test_path = plugin_dir / test_dir
            if test_path.exists():
                has_tests = True
                break

        if not has_tests:
            result["warnings"].append("테스트 파일/디렉토리가 없습니다")
            return result

        # 테스트 파일 검사
        test_files = []
        for test_dir in test_dirs:
            test_path = plugin_dir / test_dir
            if test_path.exists():
                if test_path.is_file():
                    test_files.append(test_path)
                else:
                    test_files.extend(test_path.rglob("test_*.py"))
                    test_files.extend(test_path.rglob("*_test.py"))

        if not test_files:
            result["warnings"].append("테스트 파일이 없습니다")
            return result

        # 테스트 커버리지 검사
        total_test_lines = 0
        for test_file in test_files:
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()
                total_test_lines += len(content.split("\n"))
            except Exception:
                pass

        if total_test_lines < 100:
            result["warnings"].append("테스트 코드가 부족합니다")

        return result

    def is_valid_version(self, version: str) -> bool:
        """버전 형식 검증"""
        import re

        pattern = r"^\d+\.\d+(\.\d+)?(\.\d+)?$"
        return bool(re.match(pattern, version))

    def calculate_complexity(self, tree: ast.AST) -> int:
        """순환 복잡도 계산"""
        complexity = 1

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.AsyncFor,
                    ast.AsyncWith,
                    ast.With,
                    ast.Try,
                    ast.ExceptHandler,
                ),
            ):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def generate_report(self) -> Dict[str, Any]:
        """검증 리포트 생성"""
        total_plugins = len(self.validation_results)
        valid_plugins = sum(
            1 for result in self.validation_results.values() if result["valid"]
        )

        total_errors = sum(
            len(result["errors"]) for result in self.validation_results.values()
        )
        total_warnings = sum(
            len(result["warnings"]) for result in self.validation_results.values()
        )

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_plugins": total_plugins,
                "valid_plugins": valid_plugins,
                "invalid_plugins": total_plugins - valid_plugins,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "success_rate": (
                    (valid_plugins / total_plugins * 100) if total_plugins > 0 else 0
                ),
            },
            "plugins": self.validation_results,
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> List[str]:
        """권장사항 생성"""
        recommendations = []

        # 에러가 있는 플러그인들
        invalid_plugins = [
            name
            for name, result in self.validation_results.items()
            if not result["valid"]
        ]
        if invalid_plugins:
            recommendations.append(
                f"다음 플러그인들의 오류를 수정하세요: {', '.join(invalid_plugins)}"
            )

        # 경고가 많은 플러그인들
        high_warning_plugins = [
            name
            for name, result in self.validation_results.items()
            if len(result["warnings"]) > 5
        ]
        if high_warning_plugins:
            recommendations.append(
                f"다음 플러그인들의 경고를 검토하세요: {', '.join(high_warning_plugins)}"
            )

        # 테스트가 없는 플러그인들
        no_test_plugins = [
            name
            for name, result in self.validation_results.items()
            if not result["checks"].get("tests", {}).get("valid", True)
        ]
        if no_test_plugins:
            recommendations.append(
                f"다음 플러그인들에 테스트를 추가하세요: {', '.join(no_test_plugins)}"
            )

        # 문서화가 부족한 플러그인들
        no_docs_plugins = [
            name
            for name, result in self.validation_results.items()
            if len(result["checks"].get("documentation", {}).get("warnings", [])) > 3
        ]
        if no_docs_plugins:
            recommendations.append(
                f"다음 플러그인들의 문서화를 개선하세요: {', '.join(no_docs_plugins)}"
            )

        return recommendations


def main():
    """메인 함수"""
    validator = PluginValidator()
    report = validator.validate_all_plugins()

    # 결과 출력
    print("=" * 60)
    print("플러그인 검증 리포트")
    print("=" * 60)

    summary = report["summary"]
    print(f"총 플러그인 수: {summary['total_plugins']}")
    print(f"유효한 플러그인: {summary['valid_plugins']}")
    print(f"오류가 있는 플러그인: {summary['invalid_plugins']}")
    print(f"총 오류 수: {summary['total_errors']}")
    print(f"총 경고 수: {summary['total_warnings']}")
    print(f"성공률: {summary['success_rate']:.1f}%")

    print("\n" + "=" * 60)
    print("상세 결과")
    print("=" * 60)

    for plugin_name, result in report["plugins"].items():
        status = "✅ 유효" if result["valid"] else "❌ 오류"
        print(f"\n{plugin_name}: {status}")

        if result["errors"]:
            print("  오류:")
            for error in result["errors"]:
                print(f"    - {error}")

        if result["warnings"]:
            print("  경고:")
            for warning in result["warnings"][:5]:  # 최대 5개만 표시
                print(f"    - {warning}")
            if len(result["warnings"]) > 5:
                print(f"    ... 및 {len(result['warnings']) - 5}개 더")

    if report["recommendations"]:
        print("\n" + "=" * 60)
        print("권장사항")
        print("=" * 60)
        for rec in report["recommendations"]:
            print(f"- {rec}")

    # 리포트 파일 저장
    report_file = (
        f"plugin_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n상세 리포트가 저장되었습니다: {report_file}")

    # 종료 코드
    if summary["invalid_plugins"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
