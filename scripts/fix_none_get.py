import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]


def patch_none_get(filepath):
    with open(filepath, encoding="utf-8") as f:
        code = f.read()
    # obj.get('xxx') → obj.get('xxx') if obj else None
    # 단, 이미 if obj else None이 붙은 경우는 제외
    code_new = re.sub(
        r"(\w+)\.get\(([^)]*)\)(?!\s*if\s*\1\s*else\s*None)",
        r"\1.get(\2) if \1 else None",
        code,
    )
    if code != code_new:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_new)
        print(f"[패치] {filepath}")


for target in TARGET_DIRS:
    for root, dirs, files in os.walk(target):
        for file in files:
            if file.endswith(".py"):
                patch_none_get(os.path.join(root, file))
print("[None 체크 자동 패치 완료]")
