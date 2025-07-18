import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]
UNDEFINED_VARS = ["args", "query", "config", "form", "environ"]

for target in TARGET_DIRS:
    for root, _, files in os.walk(target):
        for file in files:
            if not file.endswith(".py"):
                continue
            filepath = os.path.join(root, file)
            with open(filepath, encoding="utf-8") as f:
                code = f.read()
            # 이미 정의된 변수는 제외
            lines = code.splitlines()
            defined = set()
            for line in lines[:20]:
                for var in UNDEFINED_VARS:
                    if line.strip().startswith(f"{var} ="):
                        defined.add(var)
            # 사용되지만 정의되지 않은 변수만 상단에 추가
            to_define = []
            for var in UNDEFINED_VARS:
                if var not in defined and (f"{var}" in code):
                    to_define.append(f"{var} = None  # pyright: ignore")
            if to_define:
                code_new = "\n".join(to_define) + "\n" + code
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code_new)
                print(f"[미정의 변수 패치] {filepath}: {', '.join(to_define)}")
