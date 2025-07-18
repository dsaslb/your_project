import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]

# str | None, int | None 등 -> Optional[str], Optional[int] 변환
UNION_PATTERN = re.compile(r"(\w+)\s*\|\s*None")

# Optional import 추가
OPTIONAL_IMPORT = "from typing import Optional\n"


def patch_typehint_optional(filepath):
    with open(filepath, encoding="utf-8") as f:
        code = f.read()
    code_new = UNION_PATTERN.sub(r"Optional[\1]", code)
    # Optional import가 없으면 추가
    if "Optional[" in code_new and "from typing import Optional" not in code_new:
        code_new = OPTIONAL_IMPORT + code_new
    if code != code_new:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_new)
        print(f"[타입힌트 패치] {filepath}")


for target in TARGET_DIRS:
    for root, dirs, files in os.walk(target):
        for file in files:
            if file.endswith(".py"):
                patch_typehint_optional(os.path.join(root, file))
print("[타입힌트 Optional 변환 자동 패치 완료]")
