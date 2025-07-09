"""
ai_plugins: AI 분석, 자동화, 알림, 보고서 등 확장 플러그인 엔트리포인트
- 각 플러그인은 별도 모듈로 분리하여 동적 로딩/설정 가능
- 예시: ai_report.py, automation.py, notification_plugin.py, report_plugin.py 등
"""

# 플러그인 등록 예시
def load_plugins():
    # 추후 동적 import 및 설정 기반 로딩 구현
    return [
        "ai_report",
        "automation",
        "notification_plugin",
        "report_plugin"
    ] 