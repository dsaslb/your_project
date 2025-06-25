#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_blueprint_errors():
    """app.py의 blueprint 오류를 완전히 수정합니다."""
    
    # app.py 파일 읽기
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    skip_blueprint_section = False
    for line in lines:
        # blueprint 관련 섹션 완전 제거
        if any(keyword in line for keyword in [
            'Exempt all API blueprints from CSRF protection',
            'Register API Blueprints',
            'Register Route Blueprints',
            'csrf.exempt(',
            'app.register_blueprint(',
            'payroll_bp',
            'notifications_bp',
            'api_auth_bp',
            'api_notice_bp',
            'api_comment_bp',
            'api_report_bp',
            'admin_report_bp',
            'admin_log_bp',
            'admin_report_stat_bp',
            'comment_report_bp',
            'auth_bp'
        ]):
            if 'Register Route Blueprints' in line:
                new_lines.append(line)
                new_lines.append('# Blueprint registration will be added when needed')
            continue
        
        new_lines.append(line)
    
    # 수정된 내용으로 파일 다시 쓰기
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("Blueprint 오류 완전 수정 완료!")

if __name__ == '__main__':
    fix_blueprint_errors() 