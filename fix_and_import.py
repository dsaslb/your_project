#!/usr/bin/env python3
"""
and_ import 오류 수정 스크립트
"""


def fix_and_import_error():
    """app.py 파일의 and_ import 오류를 수정합니다."""

    # 파일 읽기
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 스케줄러 함수에서 and_ import 추가
    if "from sqlalchemy import and_, extract" not in content:
        # init_scheduler 함수 내부의 import 라인을 찾아 수정
        import_line = "from datetime import datetime, date, timedelta"
        new_import_line = "from datetime import datetime, date, timedelta\n        from sqlalchemy import and_, extract"

        content = content.replace(import_line, new_import_line)

    # 파일 쓰기
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("and_ import 오류가 수정되었습니다.")


if __name__ == "__main__":
    fix_and_import_error()
