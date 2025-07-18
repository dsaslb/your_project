#!/usr/bin/env python3
"""
신규 브랜드 생성 시 프론트엔드 폴더/페이지/샘플 데이터/설정/README/스타일 자동 생성 스크립트
- [brand_id] 템플릿 폴더를 복사하여 /frontend/app/brand/{신규_brand_id}/로 생성
- frontend_brands/의 샘플(README, 스타일, 설정 등)도 자동 복사
- 초보자/운영자도 쉽게 사용할 수 있도록 안내

사용법:
python scripts/brand_auto_generator.py --brand_id NEWBRAND --brand_name "새 브랜드명"
"""
import os
import shutil
import argparse

TEMPLATE_DIR = os.path.join('frontend', 'app', 'brand', '[brand_id]')
TARGET_BASE = os.path.join('frontend', 'app', 'brand')
BRAND_SAMPLE_BASE = 'frontend_brands/TEST'  # 샘플 브랜드 기준

README_TEMPLATE = os.path.join(BRAND_SAMPLE_BASE, 'README.md')
STYLE_TEMPLATE = os.path.join(BRAND_SAMPLE_BASE, 'styles', 'globals.css')

SAMPLE_DATA = {
    'store': [{
        'name': '샘플매장', 'address': '서울시 강남구', 'phone': '02-123-4567', 'status': 'active'
    }],
    'staff': [{
        'name': '홍길동', 'position': '매니저', 'department': '운영', 'email': 'sample@brand.com', 'phone': '010-1234-5678'
    }],
    'sales': [{
        'date': '2024-01-01', 'amount': 1000000, 'note': '샘플 매출'
    }],
    'feedback': [{
        'title': '샘플 개선요청', 'description': '매장 환경 개선 필요', 'status': 'open'
    }],
    'settings': [{
        'theme': 'default', 'color': '#FF6B6B', 'notice': '환영합니다!'
    }],
}

def create_sample_json(target_dir, subdir, data):
    sub_path = os.path.join(target_dir, subdir)
    os.makedirs(sub_path, exist_ok=True)
    sample_file = os.path.join(sub_path, 'sample.json')
    import json
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[완료] {subdir}/sample.json 생성")


def copy_brand_template(brand_id, brand_name):
    target_dir = os.path.join(TARGET_BASE, brand_id)
    if os.path.exists(target_dir):
        print(f"[경고] 이미 해당 브랜드 폴더가 존재합니다: {target_dir}")
        return
    # [brand_id] 템플릿 복사
    shutil.copytree(TEMPLATE_DIR, target_dir)
    print(f"[완료] 템플릿 폴더 복사: {target_dir}")
    # 샘플 README 복사 및 브랜드명 반영
    if os.path.exists(README_TEMPLATE):
        with open(README_TEMPLATE, 'r', encoding='utf-8') as f:
            readme = f.read().replace('테스트브랜드', brand_name)
        with open(os.path.join(target_dir, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme)
        print("[완료] README.md 생성")
    # 샘플 스타일 복사
    style_target_dir = os.path.join(target_dir, 'styles')
    os.makedirs(style_target_dir, exist_ok=True)
    if os.path.exists(STYLE_TEMPLATE):
        shutil.copy2(STYLE_TEMPLATE, os.path.join(style_target_dir, 'globals.css'))
        print("[완료] 스타일 파일 복사")
    # 샘플 데이터/설정 파일 자동 생성(필요시 확장)
    # 샘플 데이터 자동 생성
    for subdir, data in SAMPLE_DATA.items():
        create_sample_json(target_dir, subdir, data)
    print(f"[성공] 신규 브랜드({brand_id}) 폴더/페이지/샘플/데이터 자동 생성 완료!")


def main():
    parser = argparse.ArgumentParser(description='신규 브랜드 프론트엔드 폴더/페이지 자동 생성기')
    parser.add_argument('--brand_id', required=True, help='신규 브랜드 ID (예: STARBUCKS)')
    parser.add_argument('--brand_name', required=True, help='신규 브랜드명 (예: 스타벅스)')
    args = parser.parse_args()
    copy_brand_template(args.brand_id, args.brand_name)

if __name__ == '__main__':
    main() 