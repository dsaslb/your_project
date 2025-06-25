#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_app_security():
    """app.py의 중복 에러 핸들러를 수정하고 보안 기능을 추가합니다."""
    
    # app.py 파일 읽기
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    # 중복된 에러 핸들러 제거 및 보안 기능 추가
    skip_duplicate_handlers = False
    for i, line in enumerate(lines):
        # 중복된 403 핸들러 제거
        if 'def forbidden(e):' in line:
            if skip_duplicate_handlers:
                continue
            skip_duplicate_handlers = True
        
        # 중복된 413 핸들러 제거
        if 'def request_entity_too_large(e):' in line:
            if skip_duplicate_handlers:
                continue
        
        new_lines.append(line)
    
    # 보안 관련 import 추가 (파일 상단에)
    security_imports = [
        "from utils.security import (",
        "    password_strong, log_security_event, check_account_lockout,",
        "    handle_failed_login, reset_login_attempts, sanitize_input,",
        "    validate_email, validate_phone, get_client_ip, is_suspicious_request",
        ")"
    ]
    
    # import 섹션 찾기
    import_section_end = 0
    for i, line in enumerate(new_lines):
        if 'from utils.pay_transfer import transfer_salary' in line:
            import_section_end = i + 1
            break
    
    # 보안 import 추가
    for import_line in reversed(security_imports):
        new_lines.insert(import_section_end, import_line)
    
    # 로그인 라우트에 보안 기능 추가
    login_route_start = -1
    for i, line in enumerate(new_lines):
        if '@app.route(\'/login\', methods=[\'GET\', \'POST\'])' in line:
            login_route_start = i
            break
    
    if login_route_start != -1:
        # 로그인 라우트에 rate limiting 추가
        new_lines[login_route_start] = '@app.route(\'/login\', methods=[\'GET\', \'POST\'])'
        new_lines.insert(login_route_start + 1, '@limiter.limit("5 per minute")')
        new_lines.insert(login_route_start + 2, 'def login():')
    
    # 수정된 내용으로 파일 다시 쓰기
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("app.py 보안 기능 추가 완료!")

if __name__ == '__main__':
    fix_app_security() 