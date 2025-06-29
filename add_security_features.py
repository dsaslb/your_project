#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def add_security_features():
    """app.py에 보안 기능들을 추가합니다."""

    # app.py 파일 읽기
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 에러 핸들러 섹션 찾기
    if "# --- Error Handlers ---" in content:
        # 이미 존재하는 경우 업데이트
        lines = content.split("\n")
        new_lines = []

        for i, line in enumerate(lines):
            if "# --- Error Handlers ---" in line:
                new_lines.append(line)
                # 403 에러 핸들러 추가
                new_lines.append("@app.errorhandler(403)")
                new_lines.append("def forbidden(e):")
                new_lines.append("    return render_template('errors/403.html'), 403")
                new_lines.append("")
                new_lines.append("@app.errorhandler(413)")
                new_lines.append("def request_entity_too_large(e):")
                new_lines.append("    return render_template('errors/413.html'), 413")
                new_lines.append("")
                # 기존 에러 핸들러들 건너뛰기
                while i + 1 < len(lines) and not lines[i + 1].startswith("# ---"):
                    i += 1
                continue
            new_lines.append(line)

        content = "\n".join(new_lines)

    # 수정된 내용으로 파일 다시 쓰기
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("보안 기능 추가 완료!")


if __name__ == "__main__":
    add_security_features()
