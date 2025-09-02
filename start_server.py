"""
서버 시작 스크립트
동기화 시스템과 함께 Flask 서버를 시작합니다.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Flask 서버 시작"""
    print("🚀 서버 시작 중...")
    print("=" * 50)
    
    try:
        # Flask 서버 시작
        print("📡 Flask 서버 시작...")
        subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=os.path.dirname(__file__))
        
        print("✅ Flask 서버가 시작되었습니다")
        print("🌐 서버 주소: http://localhost:5000")
        print("📊 헬스체크: http://localhost:5000/healthz")
        print("🔄 동기화 API: http://localhost:5000/api/mobile/sync/batch")
        print("📈 메트릭: http://localhost:5000/metrics")
        
        # 잠시 대기
        time.sleep(2)
        
        # Outbox 워커 시작
        print("\n⚙️ Outbox 워커 시작...")
        subprocess.Popen([
            sys.executable, "start_outbox_worker.py"
        ], cwd=os.path.dirname(__file__))
        
        print("✅ Outbox 워커가 시작되었습니다")
        
        print("\n🎉 모든 서비스가 시작되었습니다!")
        print("=" * 50)
        print("📋 사용 가능한 엔드포인트:")
        print("  - GET  /healthz                    # 헬스체크")
        print("  - GET  /readyz                     # 준비 상태")
        print("  - GET  /metrics                    # 메트릭")
        print("  - POST /api/mobile/sync/batch      # 배치 동기화")
        print("  - GET  /api/mobile/sync/status     # 동기화 상태")
        print("  - GET  /api/mobile/sync/health     # 동기화 헬스체크")
        print("\n🔄 테스트 실행:")
        print("  python test_sync_system.py")
        print("\n⏹️ 서버 중지: Ctrl+C")
        
        # 메인 프로세스 대기
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ 서버 중지 중...")
            print("✅ 서버가 안전하게 중지되었습니다")
            
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        return False
    
    return True

if __name__ == '__main__':
    start_server()
