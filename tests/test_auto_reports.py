import subprocess
import os


def test_auto_daily_report():
    """
    일간 자동 보고 스크립트 정상 동작 테스트
    """
    result = subprocess.run(
        ["python", "scripts/auto_daily_report.py"], capture_output=True, text=True
    )
    assert "일간 리포트 이메일 발송 완료" in result.stdout


def test_auto_weekly_report():
    """
    주간 자동 보고 스크립트 정상 동작 테스트
    """
    result = subprocess.run(
        ["python", "scripts/auto_weekly_report.py"], capture_output=True, text=True
    )
    assert "주간 리포트 이메일 발송 완료" in result.stdout
