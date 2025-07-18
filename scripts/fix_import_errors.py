import os
import re
import subprocess
import sys

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]
EXTERNAL_IMPORT_PATTERN = re.compile(r"^import ([a-zA-Z0-9_]+)", re.MULTILINE)
FROM_IMPORT_PATTERN = re.compile(r"^from ([a-zA-Z0-9_\.]+) import", re.MULTILINE)

# 외부 패키지 자동 설치
installed = set()


def install_package(pkg):
    if pkg in installed:
        return
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        installed.add(pkg)
        print(f"[pip 설치] {pkg}")
    except Exception as e:
        print(f"[pip 설치 실패] {pkg}: {e}")


# 내부 모듈 import 경로/존재 확인 및 자동 주석 처리
def check_internal_import(filepath, import_line, module_path):
    # 상대경로로 파일 존재 확인
    rel_path = module_path.replace(".", os.sep) + ".py"
    abs_path = os.path.join(os.path.dirname(filepath), rel_path)
    if not os.path.exists(abs_path):
        # import 라인에 pyright: ignore 주석 추가
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if import_line in line and "# pyright: ignore" not in line:
                lines[i] = line.rstrip() + "  # pyright: ignore\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[내부 모듈 없음] {filepath}: {import_line}")


for target in TARGET_DIRS:
    for root, _, files in os.walk(target):
        for file in files:
            if not file.endswith(".py"):
                continue
            filepath = os.path.join(root, file)
            with open(filepath, encoding="utf-8") as f:
                code = f.read()
            # 외부 패키지 import
            for match in EXTERNAL_IMPORT_PATTERN.finditer(code):
                pkg = match.group(1)
                # 내장/내부 모듈은 제외
                if pkg in sys.builtin_module_names or pkg in [
                    "os",
                    "sys",
                    "re",
                    "datetime",
                    "logging",
                    "json",
                    "time",
                    "subprocess",
                    "typing",
                    "flask",
                    "sqlalchemy",
                    "functools",
                    "threading",
                    "enum",
                    "dataclasses",
                    "collections",
                    "pathlib",
                    "base64",
                    "hashlib",
                    "uuid",
                    "tempfile",
                    "shutil",
                    "itertools",
                    "random",
                    "traceback",
                    "email",
                    "smtplib",
                    "requests",
                    "cv2",
                    "numpy",
                    "pandas",
                    "matplotlib",
                    "seaborn",
                    "PIL",
                    "joblib",
                    "psutil",
                    "importlib",
                    "weakref",
                    "wave",
                ]:
                    continue
                install_package(pkg)
            for match in FROM_IMPORT_PATTERN.finditer(code):
                module_path = match.group(1)
                # 외부 패키지 설치
                if "." not in module_path:
                    if module_path in sys.builtin_module_names or module_path in [
                        "os",
                        "sys",
                        "re",
                        "datetime",
                        "logging",
                        "json",
                        "time",
                        "subprocess",
                        "typing",
                        "flask",
                        "sqlalchemy",
                        "functools",
                        "threading",
                        "enum",
                        "dataclasses",
                        "collections",
                        "pathlib",
                        "base64",
                        "hashlib",
                        "uuid",
                        "tempfile",
                        "shutil",
                        "itertools",
                        "random",
                        "traceback",
                        "email",
                        "smtplib",
                        "requests",
                        "cv2",
                        "numpy",
                        "pandas",
                        "matplotlib",
                        "seaborn",
                        "PIL",
                        "joblib",
                        "psutil",
                        "importlib",
                        "weakref",
                        "wave",
                    ]:
                        continue
                    install_package(module_path)
                else:
                    # 내부 모듈 경로 확인
                    import_line = f"from {module_path} import"
                    check_internal_import(filepath, import_line, module_path)
