import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]
AUTO_IMPORTS = {
    "jsonify": "from flask import jsonify",
    "current_app": "from flask import current_app",
    "Blueprint": "from flask import Blueprint",
    "request": "from flask import request",
    "url_for": "from flask import url_for",
    "flash": "from flask import flash",
}

for target in TARGET_DIRS:
    for root, _, files in os.walk(target):
        for file in files:
            if not file.endswith(".py"):
                continue
            filepath = os.path.join(root, file)
            with open(filepath, encoding="utf-8") as f:
                code = f.read()
            lines = code.splitlines()
            # 이미 import된 경우는 제외
            already_imported = set()
            for line in lines[:20]:
                for key, imp in AUTO_IMPORTS.items():
                    if key in line or imp in line:
                        already_imported.add(key)
            # 사용됐지만 import 없는 경우 상단에 추가
            to_import = []
            for key, imp in AUTO_IMPORTS.items():
                if key in code and key not in already_imported:
                    to_import.append(imp)
            if to_import:
                code_new = "\n".join(to_import) + "\n" + code
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code_new)
                print(f"[자동 import 추가] {filepath}: {', '.join(to_import)}")
