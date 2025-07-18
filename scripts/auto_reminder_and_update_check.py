# -*- coding: utf-8 -*-
"""
[자동 리마인드/업데이트 점검 스크립트 샘플]
- 주요 문서(README, 가이드, FAQ, 접근성, 테스트, 자동화 스크립트 등) 최종 수정일/미점검 항목 자동 알림
- 초보자/운영자도 쉽게 확장/문의할 수 있도록 주석/문의 안내 포함
- 문의: support@example.com

[사용법]
- python scripts/auto_reminder_and_update_check.py
"""
import os
import time
import datetime

CHECK_FILES = [
    'README.md',
    'docs/ADMIN_OPERATION_GUIDE.md',
    'frontend/app/accessibility/page.tsx',
    'frontend/app/faq/page.tsx',
    'scripts/auto_report_and_alert.py',
    'scripts/auto_env_check_and_notify.py',
]

REMIND_DAYS = 30  # 30일 이상 미수정 시 알림

def check_file_updates():
    now = time.time()
    reminders = []
    for f in CHECK_FILES:
        if not os.path.exists(f):
            reminders.append(f'파일 없음: {f}')
            continue
        mtime = os.path.getmtime(f)
        days = int((now - mtime) // 86400)
        if days >= REMIND_DAYS:
            dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            reminders.append(f'{f} - {days}일 미수정 (최종: {dt})')
    return reminders

if __name__ == '__main__':
    reminders = check_file_updates()
    if reminders:
        print('[자동 리마인드] 미점검/미최신화 파일:', *reminders, sep='\n- ')
    else:
        print('[자동 리마인드] 모든 주요 파일이 최근에 점검/최신화됨') 