#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
중복 라우트 제거 스크립트
"""

def fix_duplicate_routes():
    """app.py에서 중복된 라우트를 제거합니다."""
    
    print("🔧 중복 라우트 제거 중...")
    
    # 파일 읽기
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    seen_routes = set()
    skip_duplicates = set()
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # 라우트 정의 라인인지 확인
        if line_stripped.startswith('@app.route('):
            # 라우트 경로 추출
            route_path = line_stripped.split("'")[1] if "'" in line_stripped else line_stripped.split('"')[1]
            
            if route_path in seen_routes:
                print(f"중복 라우트 발견: {route_path}")
                skip_duplicates.add(route_path)
                # 이 라우트와 다음 함수 정의까지 건너뛰기
                continue
            else:
                seen_routes.add(route_path)
        
        # 중복된 라우트의 함수 정의 부분 건너뛰기
        if skip_duplicates and line_stripped.startswith('def ') and 'notice_unhide' in line_stripped:
            # 함수 정의 시작부터 다음 라우트까지 건너뛰기
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('@app.route('):
                j += 1
            # 건너뛴 라인들 표시
            print(f"제거된 중복 함수: {line_stripped}")
            continue
        
        new_lines.append(line)
    
    # 파일 저장
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ 중복 라우트 제거 완료!")

if __name__ == '__main__':
    fix_duplicate_routes() 