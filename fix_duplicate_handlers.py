#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_duplicate_handlers():
    """app.py의 중복된 에러 핸들러를 제거합니다."""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    # 중복된 핸들러 제거
    skip_duplicates = False
    for line in lines:
        if 'def forbidden(e):' in line:
            if skip_duplicates:
                continue
            skip_duplicates = True
        
        if 'def request_entity_too_large(e):' in line:
            if skip_duplicates:
                continue
        
        new_lines.append(line)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("중복된 에러 핸들러 제거 완료!")

if __name__ == '__main__':
    fix_duplicate_handlers() 