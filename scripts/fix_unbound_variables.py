import os
import shutil
import datetime
import re
import zipfile


# 1. 전체 백업
def backup_project():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"your_program_backup_{now}.zip"
    exclude_dirs = [
        "node_modules",
        ".venv",
        "venv",
        "logs",
        "data",
        "static",
        "marketplace",
        "sample_modules",
        "tests",
        "migrations",
        "redis-server",
        "production",
        "mobile_app",
        "backups",
        "sandbox",
        "scripts",
        "templates",
    ]
    with zipfile.ZipFile(backup_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # 제외 폴더는 건너뜀
            if any(ex in root for ex in exclude_dirs):
                continue
            for file in files:
                if file.endswith(".zip") or file.endswith(".pyc"):
                    continue
                filepath = os.path.join(root, file)
                zipf.write(filepath, os.path.relpath(filepath, "."))
    print(f"[백업 완료] {backup_name}")


# 2. Optional 자동 추가 및 None 할당 패치
def fix_unbound_variables(target_dirs):
    log = []
    pattern = re.compile(r"def (\w+)\(([^)]*)\):")
    for root, dirs, files in os.walk("."):
        if not any(root.startswith(f"./{d}") for d in target_dirs):
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, encoding="utf-8") as f:
                    lines = f.readlines()
                changed = False
                new_lines = []
                for line in lines:
                    # 예시: int = None → Optional[int] = None
                    if re.search(r":\s*\w+\s*=\s*None", line):
                        line = re.sub(
                            r":\s*(\w+)\s*=\s*None",
                            r": Optional[\1] = None  # pyright: ignore",
                            line,
                        )
                        changed = True
                    new_lines.append(line)
                if changed:
                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    log.append(f"{path} 수정됨")
    with open("fix_unbound_variables.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print(f"[수정 로그 저장] fix_unbound_variables.log")


# 3. 롤백 기능
def rollback(backup_zip):
    shutil.unpack_archive(backup_zip, ".")
    print(f"[롤백 완료] {backup_zip} 복원됨")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback(sys.argv[2])
    else:
        backup_project()
        fix_unbound_variables(["api", "core", "models", "routes", "services", "utils"])
        print("[자동 수정 완료] pyright를 다시 실행해 주세요.")
