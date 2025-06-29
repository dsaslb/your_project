#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def fix_app_imports():
    """app.py의 import 오류를 수정합니다."""

    # app.py 파일 읽기
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 문제가 되는 blueprint 관련 코드 제거
    lines = content.split("\n")
    new_lines = []

    skip_section = False
    for line in lines:
        # blueprint 관련 섹션 건너뛰기
        if "Exempt all API blueprints from CSRF protection" in line:
            skip_section = True
            continue
        elif "Register Route Blueprints" in line:
            skip_section = False
            new_lines.append(line)
            continue
        elif skip_section:
            continue

        new_lines.append(line)

    # 수정된 내용으로 파일 다시 쓰기
    with open("app.py", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print("app.py import 오류 수정 완료!")


if __name__ == "__main__":
    fix_app_imports()
