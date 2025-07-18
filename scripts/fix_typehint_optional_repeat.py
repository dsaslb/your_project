import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]
# 함수 인자/리턴 타입에서 str, int, Dict 등 + None → Optional[...] 변환
UNION_PATTERN = re.compile(r"(\w+)\s*\|\s*None")
# 기본값이 None인데 Optional이 아닌 경우
DEF_PATTERN = re.compile(
    r"(def [\w_]+\(.*?)([\w_]+): (str|int|float|dict|list|Dict|List|Any)( = None)",
    re.DOTALL,
)

OPTIONAL_IMPORT = "from typing import Optional\n"


def patch_typehint_optional(filepath):
    with open(filepath, encoding="utf-8") as f:
        code = f.read()
    code_new = UNION_PATTERN.sub(r"Optional[\1]", code)
    code_new = DEF_PATTERN.sub(
        lambda m: m.group(1)
        + m.group(2)
        + ": Optional["
        + m.group(3)
        + "]"
        + m.group(4),
        code_new,
    )
    # Optional import가 없으면 추가
    if "Optional[" in code_new and "from typing import Optional" not in code_new:
        code_new = OPTIONAL_IMPORT + code_new
    if code != code_new:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_new)
        print(f"[Optional 타입힌트 반복 패치] {filepath}")


for target in TARGET_DIRS:
    for root, _, files in os.walk(target):
        for file in files:
            if not file.endswith(".py"):
                continue
            patch_typehint_optional(os.path.join(root, file))
