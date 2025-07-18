import os
import re

TARGET_DIRS = ["api", "core", "models", "routes", "services", "utils"]
# 함수 정의 패턴: def func(a, b, c):
DEF_PATTERN = re.compile(r"def (\w+)\((.*?)\):", re.DOTALL)
# 함수 호출 패턴: func(a=1, b=2)
CALL_PATTERN = re.compile(r"(\w+)\((.*?)\)")


def get_param_names(params):
    # a, b=1, c: int = None 등에서 이름만 추출
    return [
        p.split(":")[0].split("=")[0].strip() for p in params.split(",") if p.strip()
    ]


def patch_param_name_mismatch(filepath):
    with open(filepath, encoding="utf-8") as f:
        code = f.read()
    # 함수 정의 파라미터 추출
    defs = {m.group(1): get_param_names(m.group(2)) for m in DEF_PATTERN.finditer(code)}

    # 함수 호출 파라미터 추출 및 수정
    def repl_call(m):
        fname, args = m.group(1), m.group(2)
        if fname in defs:
            call_args = args.split(",")
            def_args = defs[fname]
            new_args = []
            for i, arg in enumerate(call_args):
                if "=" in arg and i < len(def_args):
                    # 파라미터명 일치화
                    new_args.append(f'{def_args[i]}={arg.split("=",1)[1].strip()}')
                else:
                    new_args.append(arg)
            return f'{fname}({", ".join(new_args)})'
        return m.group(0)

    code_new = CALL_PATTERN.sub(repl_call, code)
    if code != code_new:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_new)
        print(f"[파라미터명 자동 일치] {filepath}")


for target in TARGET_DIRS:
    for root, _, files in os.walk(target):
        for file in files:
            if not file.endswith(".py"):
                continue
            patch_param_name_mismatch(os.path.join(root, file))
