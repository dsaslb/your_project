#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOM(U+FEFF) 제거 스크립트
"""

import os
import sys

def remove_bom_from_file(file_path):
    """파일에서 BOM(U+FEFF) 문자를 제거합니다."""
    try:
        # 파일을 바이너리 모드로 읽기
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # BOM 제거
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
            print(f"BOM 제거됨: {file_path}")
        else:
            print(f"BOM 없음: {file_path}")
            return False
        
        # UTF-8로 다시 저장
        with open(file_path, 'wb') as f:
            f.write(content)
        
        print(f"파일 저장 완료: {file_path}")
        return True
        
    except Exception as e:
        print(f"오류 발생: {file_path} - {e}")
        return False

def main():
    # 프로젝트 루트로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # BOM 제거할 파일 목록
    files_to_check = [
        'api/staff.py',
        'api/security_enhanced.py',
        'api/brand_management.py'
    ]
    
    print("BOM 제거 시작...")
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            remove_bom_from_file(file_path)
        else:
            print(f"파일 없음: {file_path}")
    
    print("BOM 제거 완료!")

if __name__ == "__main__":
    main() 