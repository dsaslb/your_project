#!/usr/bin/env python3
"""
모든 서비스 시작 스크립트
"""

import subprocess
import time
import threading
import signal
import sys
import os
from datetime import datetime

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.is_running = True
        
    def start_backend_server(self):
        """백엔드 서버 시작"""
        print("🚀 백엔드 서버 시작 중...")
        try:
            # PowerShell에서 Python 명령 실행
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    [sys.executable, "simple_test_server.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            else:  # Unix/Linux
                process = subprocess.Popen(
                    [sys.executable, "simple_test_server.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            self.processes['backend'] = process
            print("✅ 백엔드 서버가 시작되었습니다. (포트: 5000)")
            return True
        except Exception as e:
            print(f"❌ 백엔드 서버 시작 실패: {e}")
            return False
            
    def start_frontend_server(self):
        """프론트엔드 서버 시작"""
        print("🚀 프론트엔드 서버 시작 중...")
        try:
            # PowerShell에서 npm 명령 실행
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd='frontend',
                    shell=True
                )
            else:  # Unix/Linux
                process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd='frontend'
                )
            
            self.processes['frontend'] = process
            print("✅ 프론트엔드 서버가 시작되었습니다. (포트: 3000)")
            return True
        except Exception as e:
            print(f"❌ 프론트엔드 서버 시작 실패: {e}")
            return False
            
    def start_performance_monitor(self):
        """성능 모니터링 시작"""
        print("🚀 성능 모니터링 시작 중...")
        try:
            process = subprocess.Popen(
                [sys.executable, "monitoring/performance-monitor.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['monitor'] = process
            print("✅ 성능 모니터링이 시작되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 성능 모니터링 시작 실패: {e}")
            return False
            
    def start_swagger_server(self):
        """Swagger 문서 서버 시작"""
        print("🚀 Swagger 문서 서버 시작 중...")
        try:
            process = subprocess.Popen(
                [sys.executable, "swagger_docs.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['swagger'] = process
            print("✅ Swagger 문서 서버가 시작되었습니다. (포트: 5001)")
            return True
        except Exception as e:
            print(f"❌ Swagger 서버 시작 실패: {e}")
            return False
            
    def monitor_process(self, name, process):
        """프로세스 모니터링"""
        while self.is_running and process.poll() is None:
            time.sleep(1)
            
        if self.is_running:
            print(f"⚠️  {name} 서비스가 종료되었습니다.")
            
    def start_all_services(self):
        """모든 서비스 시작"""
        print("=" * 60)
        print("🚀 Your Program 전체 서비스 시작")
        print("=" * 60)
        
        # 백엔드 서버 시작
        if not self.start_backend_server():
            return False
            
        # 잠시 대기
        time.sleep(3)
        
        # 프론트엔드 서버 시작
        if not self.start_frontend_server():
            return False
            
        # 성능 모니터링 시작
        self.start_performance_monitor()
        
        # Swagger 서버 시작
        self.start_swagger_server()
        
        # 프로세스 모니터링 시작
        for name, process in self.processes.items():
            thread = threading.Thread(target=self.monitor_process, args=(name, process))
            thread.daemon = True
            thread.start()
            
        print("\n" + "=" * 60)
        print("🎉 모든 서비스가 시작되었습니다!")
        print("=" * 60)
        print("\n📋 접속 정보:")
        print("  🌐 프론트엔드: http://localhost:3000")
        print("  🔧 백엔드 API: http://localhost:5000")
        print("  📚 Swagger 문서: http://localhost:5000/swagger-ui")
        print("  📊 성능 모니터링: monitoring/performance.log")
        print("\n🔑 테스트 계정:")
        print("  아이디: admin")
        print("  비밀번호: admin123")
        print("\n⏹️  종료하려면 Ctrl+C를 누르세요.")
        print("=" * 60)
        
        return True
        
    def stop_all_services(self):
        """모든 서비스 중지"""
        print("\n🛑 서비스 종료 중...")
        self.is_running = False
        
        for name, process in self.processes.items():
            try:
                print(f"  {name} 서비스 종료 중...")
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ {name} 서비스가 종료되었습니다.")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  {name} 서비스를 강제 종료합니다.")
                process.kill()
            except Exception as e:
                print(f"  ❌ {name} 서비스 종료 실패: {e}")
                
        print("✅ 모든 서비스가 종료되었습니다.")
        
    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"\n📡 시그널 {signum} 수신. 서비스를 종료합니다.")
        self.stop_all_services()
        sys.exit(0)

def main():
    """메인 함수"""
    manager = ServiceManager()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        # 모든 서비스 시작
        if manager.start_all_services():
            # 서비스가 실행 중인 동안 대기
            while manager.is_running:
                time.sleep(1)
        else:
            print("❌ 서비스 시작에 실패했습니다.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다.")
        manager.stop_all_services()
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        manager.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main() 