import os

TARGET_EXT = ".py"
OLD = "from models import "
NEW = "from models_main import "

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(TARGET_EXT) and file != os.path.basename(__file__):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if OLD in content:
                    new_content = content.replace(OLD, NEW)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"[수정됨] {path}")
            except Exception as e:
                print(f"[오류] {path}: {e}")
