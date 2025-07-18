import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]
# None 접근 위험 패턴
PATTERNS = [
    (re.compile(r"(\w+)\.get\("), "{obj}.get({args}) if {obj} else None"),
    (
        re.compile(r"for (\w+) in (\w+):"),
        "for {var} in {iterable} if {iterable} is not None:",
    ),
    (re.compile(r"(\w+)\[(.+?)\]"), "{obj}[{key}] if {obj} is not None else None"),
    (re.compile(r"(\w+)\.strip\(\)"), "{obj}.strip() if {obj} is not None else ''"),
    (re.compile(r"(\w+)\.value"), "{obj}.value if {obj} is not None else None"),
    (re.compile(r"(\w+)\.lower\(\)"), "{obj}.lower() if {obj} is not None else ''"),
    (re.compile(r"(\w+)\.items\(\)"), "{obj}.items() if {obj} is not None else []"),
]


def patch_none_access(filepath):
    with open(filepath, encoding="utf-8") as f:
        code = f.read()
    code_new = code
    for pattern, repl in PATTERNS:
        # 단순 치환(정교한 AST 변환은 아님)
        code_new = pattern.sub(
            lambda m: repl.format(
                obj=m.group(1),
                args=m.group(0).split("(", 1)[1][:-1] if "(" in m.group(0) else "",
                var=m.group(1),
                iterable=m.group(2) if len(m.groups()) > 1 else "",
                key=m.group(2) if len(m.groups()) > 1 else "",
            ),
            code_new,
        )
    if code != code_new:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_new)
        print(f"[None 접근 패치] {filepath}")


for target in TARGET_DIRS:
    for root, _, files in os.walk(target):
        for file in files:
            if not file.endswith(".py"):
                continue
            patch_none_access(os.path.join(root, file))
