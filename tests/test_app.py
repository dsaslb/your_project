#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 앱 import 테스트 스크립트
"""

try:
    print("🔍 Flask 앱 import 시도...")
    from app import app
    print("✅ Flask 앱 import 성공!")
    
    print("\n🔍 등록된 블루프린트:")
    for bp_name, bp in app.blueprints.items():
        print(f"  - {bp_name}: {bp.url_prefix}")
    
    print("\n🔍 등록된 라우트:")
    for rule in app.url_map.iter_rules():
        print(f"  - {rule.rule} [{', '.join(rule.methods)}]")
    
    print("\n✅ 모든 테스트 통과!")
    
except Exception as e:
    print(f"❌ Flask 앱 import 실패: {e}")
    import traceback
    traceback.print_exc()
