#!/usr/bin/env python3
"""
플러그인 보안 시스템 초기화 스크립트
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.backend.plugin_security_system import PluginSecuritySystem

def init_plugin_security_system():
    """플러그인 보안 시스템 초기화"""
    print("🔐 플러그인 보안 시스템 초기화 시작...")
    
    # 보안 시스템 인스턴스 생성
    security_system = PluginSecuritySystem()
    
    # 샘플 보안 정책 생성
    print("📋 샘플 보안 정책 생성 중...")
    sample_policies = [
        {
            'plugin_id': 'your_program_management',
            'security_level': 'high',
            'allowed_ips': ['127.0.0.1', '192.168.1.0/24'],
            'allowed_domains': ['localhost', 'your-program.local'],
            'max_requests_per_minute': 200,
            'require_authentication': True,
            'require_authorization': True,
            'allowed_permissions': ['read', 'write', 'admin']
        },
        {
            'plugin_id': 'analytics_plugin',
            'security_level': 'medium',
            'allowed_ips': ['127.0.0.1'],
            'allowed_domains': ['localhost'],
            'max_requests_per_minute': 100,
            'require_authentication': True,
            'require_authorization': False,
            'allowed_permissions': ['read']
        },
        {
            'plugin_id': 'notification_plugin',
            'security_level': 'low',
            'allowed_ips': [],
            'allowed_domains': [],
            'max_requests_per_minute': 50,
            'require_authentication': False,
            'require_authorization': False,
            'allowed_permissions': ['read']
        }
    ]
    
    for policy_data in sample_policies:
        success = security_system.create_security_policy(
            policy_data['plugin_id'], 
            policy_data
        )
        if success:
            print(f"  ✅ {policy_data['plugin_id']} 보안 정책 생성 완료")
        else:
            print(f"  ⚠️  {policy_data['plugin_id']} 보안 정책 생성 실패 (이미 존재)")
    
    # 샘플 API 키 생성
    print("🔑 샘플 API 키 생성 중...")
    sample_api_keys = [
        {
            'plugin_id': 'your_program_management',
            'name': '관리자 API 키',
            'permissions': ['read', 'write', 'admin'],
            'expires_in_days': 365
        },
        {
            'plugin_id': 'your_program_management',
            'name': '읽기 전용 API 키',
            'permissions': ['read'],
            'expires_in_days': 30
        },
        {
            'plugin_id': 'analytics_plugin',
            'name': '분석 API 키',
            'permissions': ['read'],
            'expires_in_days': 90
        }
    ]
    
    generated_keys = []
    for key_data in sample_api_keys:
        api_key = security_system.generate_api_key(
            key_data['plugin_id'],
            key_data['name'],
            key_data['permissions'],
            key_data['expires_in_days']
        )
        if api_key:
            generated_keys.append({
                'name': key_data['name'],
                'plugin_id': key_data['plugin_id'],
                'api_key': api_key
            })
            print(f"  ✅ {key_data['name']} 생성 완료")
        else:
            print(f"  ❌ {key_data['name']} 생성 실패")
    
    # 샘플 감사 로그 생성
    print("📝 샘플 감사 로그 생성 중...")
    sample_audit_events = [
        {
            'plugin_id': 'your_program_management',
            'user_id': 'admin',
            'action': 'plugin_access',
            'resource': '/api/restaurant/orders',
            'ip_address': '127.0.0.1',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'success': True,
            'details': {'method': 'GET', 'status_code': 200}
        },
        {
            'plugin_id': 'your_program_management',
            'user_id': 'user1',
            'action': 'api_key_validation',
            'resource': '/api/restaurant/inventory',
            'ip_address': '192.168.1.100',
            'user_agent': 'Python/3.9 requests/2.25.1',
            'success': True,
            'details': {'api_key_id': 'sample_key_1'}
        },
        {
            'plugin_id': 'analytics_plugin',
            'user_id': 'analyst',
            'action': 'data_export',
            'resource': '/api/analytics/reports',
            'ip_address': '10.0.0.50',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'success': False,
            'details': {'error': '권한 부족', 'required_permission': 'admin'}
        }
    ]
    
    for event in sample_audit_events:
        success = security_system.log_security_event(
            event['plugin_id'],
            event['user_id'],
            event['action'],
            event['resource'],
            event['ip_address'],
            event['user_agent'],
            event['success'],
            event['details']
        )
        if success:
            print(f"  ✅ {event['action']} 감사 로그 생성 완료")
        else:
            print(f"  ❌ {event['action']} 감사 로그 생성 실패")
    
    # 샘플 취약점 보고서 생성
    print("⚠️  샘플 취약점 보고서 생성 중...")
    sample_vulnerabilities = [
        {
            'plugin_id': 'your_program_management',
            'severity': 'medium',
            'title': '하드코딩된 비밀번호 발견',
            'description': '설정 파일에서 하드코딩된 데이터베이스 비밀번호가 발견되었습니다.',
            'cve_id': None,
            'affected_versions': ['1.0.0', '1.1.0'],
            'fixed_versions': ['1.2.0'],
            'remediation': '환경 변수를 사용하여 비밀번호를 관리하세요.',
            'status': 'open'
        },
        {
            'plugin_id': 'analytics_plugin',
            'severity': 'low',
            'title': '불필요한 디버그 로그',
            'description': '프로덕션 환경에서 디버그 로그가 활성화되어 있습니다.',
            'cve_id': None,
            'affected_versions': ['2.0.0'],
            'fixed_versions': [],
            'remediation': '프로덕션 환경에서 디버그 로그를 비활성화하세요.',
            'status': 'ignored'
        },
        {
            'plugin_id': 'notification_plugin',
            'severity': 'high',
            'title': 'SQL 인젝션 취약점',
            'description': '사용자 입력이 SQL 쿼리에 직접 삽입되어 SQL 인젝션 공격에 취약합니다.',
            'cve_id': 'CVE-2023-1234',
            'affected_versions': ['1.0.0'],
            'fixed_versions': ['1.1.0'],
            'remediation': '매개변수화된 쿼리를 사용하세요.',
            'status': 'fixed'
        }
    ]
    
    # 취약점 데이터를 직접 저장
    vulnerabilities_file = Path("plugin_security/vulnerabilities.json")
    if vulnerabilities_file.exists():
        with open(vulnerabilities_file, 'r', encoding='utf-8') as f:
            existing_vulns = json.load(f)
    else:
        existing_vulns = []
    
    for vuln_data in sample_vulnerabilities:
        vulnerability = {
            'report_id': f"vuln_{len(existing_vulns) + 1}",
            'plugin_id': vuln_data['plugin_id'],
            'severity': vuln_data['severity'],
            'title': vuln_data['title'],
            'description': vuln_data['description'],
            'cve_id': vuln_data['cve_id'],
            'affected_versions': vuln_data['affected_versions'],
            'fixed_versions': vuln_data['fixed_versions'],
            'remediation': vuln_data['remediation'],
            'discovered_at': datetime.now().isoformat(),
            'status': vuln_data['status']
        }
        existing_vulns.append(vulnerability)
        print(f"  ✅ {vuln_data['title']} 취약점 보고서 생성 완료")
    
    with open(vulnerabilities_file, 'w', encoding='utf-8') as f:
        json.dump(existing_vulns, f, indent=2, ensure_ascii=False)
    
    # 생성된 API 키 정보 출력
    print("\n🔑 생성된 API 키 정보:")
    print("=" * 50)
    for key_info in generated_keys:
        print(f"플러그인: {key_info['plugin_id']}")
        print(f"이름: {key_info['name']}")
        print(f"API 키: {key_info['api_key']}")
        print("-" * 30)
    
    print("\n✅ 플러그인 보안 시스템 초기화 완료!")
    print("\n📋 다음 기능들을 사용할 수 있습니다:")
    print("  • 보안 정책 관리")
    print("  • API 키 생성 및 관리")
    print("  • 감사 로그 조회")
    print("  • 취약점 스캔 및 관리")
    print("  • 권한 확인")
    
    return True

if __name__ == "__main__":
    try:
        init_plugin_security_system()
    except Exception as e:
        print(f"❌ 초기화 중 오류 발생: {e}")
        sys.exit(1) 
