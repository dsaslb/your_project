#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def fix_413_handler():
    """app.py의 413 에러 핸들러 함수 이름을 수정합니다."""

    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 413 에러 핸들러 수정
    content = content.replace(
        "@app.errorhandler(413)\n    return render_template('errors/413.html'), 413",
        "@app.errorhandler(413)\ndef request_entity_too_large(e):\n    return render_template('errors/413.html'), 413",
    )

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("413 에러 핸들러 수정 완료!")


if __name__ == "__main__":
    fix_413_handler()
