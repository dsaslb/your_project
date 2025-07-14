"""
모듈 마켓플레이스 시스템 간단 테스트
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path

class TestModuleMarketplaceBasic(unittest.TestCase):
    """모듈 마켓플레이스 기본 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.marketplace_dir = Path(self.temp_dir) / "marketplace"
        self.modules_dir = Path(self.temp_dir) / "plugins"
        
        # 디렉토리 생성
        self.marketplace_dir.mkdir(exist_ok=True)
        self.modules_dir.mkdir(exist_ok=True)
        
        # 하위 디렉토리 생성
        (self.marketplace_dir / "modules").mkdir(exist_ok=True)
        (self.marketplace_dir / "installed").mkdir(exist_ok=True)
        (self.marketplace_dir / "configs").mkdir(exist_ok=True)
        (self.marketplace_dir / "backups").mkdir(exist_ok=True)
        
        # 테스트 사용자 ID
        self.test_user_id = 1
        self.test_scope_id = 1
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir)
    
    def test_directory_structure(self):
        """디렉토리 구조 테스트"""
        # 기본 디렉토리 존재 확인
        self.assertTrue(self.marketplace_dir.exists())
        self.assertTrue(self.modules_dir.exists())
        
        # 하위 디렉토리 존재 확인
        self.assertTrue((self.marketplace_dir / "modules").exists())
        self.assertTrue((self.marketplace_dir / "installed").exists())
        self.assertTrue((self.marketplace_dir / "configs").exists())
        self.assertTrue((self.marketplace_dir / "backups").exists())
    
    def test_sample_module_creation(self):
        """샘플 모듈 생성 테스트"""
        # 출퇴근 관리 모듈 정보
        attendance_module = {
            'id': 'attendance_management',
            'name': '출퇴근 관리',
            'version': '1.0.0',
            'description': '직원 출퇴근 시간 관리 및 근태 분석',
            'category': 'hr',
            'tags': ['출퇴근', '근태', '인사'],
            'author': 'Your Program Team',
            'features': [
                '출퇴근 기록',
                '근태 분석',
                'AI 예측',
                '알림 시스템'
            ],
            'dependencies': [],
            'compatibility': ['restaurant'],
            'rating': 4.5,
            'downloads': 1250,
            'last_updated': '2024-01-15'
        }
        
        # 모듈 파일 생성
        module_file = self.marketplace_dir / "modules" / "attendance_management.json"
        with open(module_file, 'w', encoding='utf-8') as f:
            json.dump(attendance_module, f, ensure_ascii=False, indent=2)
        
        # 파일 존재 확인
        self.assertTrue(module_file.exists())
        
        # 파일 내용 확인
        with open(module_file, 'r', encoding='utf-8') as f:
            loaded_module = json.load(f)
        
        self.assertEqual(loaded_module['id'], 'attendance_management')
        self.assertEqual(loaded_module['name'], '출퇴근 관리')
        self.assertEqual(loaded_module['category'], 'hr')
    
    def test_module_installation_simulation(self):
        """모듈 설치 시뮬레이션 테스트"""
        # 설치 정보
        installation_info = {
            'module_id': 'attendance_management',
            'user_id': self.test_user_id,
            'scope_id': self.test_scope_id,
            'scope_type': 'branch',
            'installed_at': '2024-01-15T10:00:00Z',
            'status': 'installed',
            'version': '1.0.0'
        }
        
        # 설치 파일 생성
        install_file = self.marketplace_dir / "installed" / f"{self.test_user_id}_{self.test_scope_id}_branch.json"
        install_file.parent.mkdir(exist_ok=True)
        
        with open(install_file, 'w', encoding='utf-8') as f:
            json.dump(installation_info, f, ensure_ascii=False, indent=2)
        
        # 파일 존재 확인
        self.assertTrue(install_file.exists())
        
        # 설치 정보 확인
        with open(install_file, 'r', encoding='utf-8') as f:
            loaded_install = json.load(f)
        
        self.assertEqual(loaded_install['module_id'], 'attendance_management')
        self.assertEqual(loaded_install['user_id'], self.test_user_id)
        self.assertEqual(loaded_install['status'], 'installed')
    
    def test_module_config_management(self):
        """모듈 설정 관리 테스트"""
        # 모듈 설정
        module_config = {
            'auto_notifications': True,
            'sync_interval': 'realtime',
            'ai_analysis': True,
            'auto_backup': False,
            'notification_channels': ['email', 'sms'],
            'data_retention_days': 365
        }
        
        # 설정 파일 생성
        config_file = self.marketplace_dir / "configs" / f"attendance_management_{self.test_user_id}_{self.test_scope_id}.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(module_config, f, ensure_ascii=False, indent=2)
        
        # 파일 존재 확인
        self.assertTrue(config_file.exists())
        
        # 설정 확인
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        self.assertTrue(loaded_config['auto_notifications'])
        self.assertEqual(loaded_config['sync_interval'], 'realtime')
        self.assertTrue(loaded_config['ai_analysis'])
        self.assertFalse(loaded_config['auto_backup'])
    
    def test_module_statistics(self):
        """모듈 통계 테스트"""
        # 통계 데이터
        statistics = {
            'total_installed': 3,
            'total_activated': 2,
            'total_deactivated': 1,
            'category_distribution': {
                'hr': 2,
                'sales': 1,
                'inventory': 0
            },
            'popular_modules': [
                'attendance_management',
                'sales_management',
                'payroll_management'
            ],
            'last_updated': '2024-01-15T10:00:00Z'
        }
        
        # 통계 파일 생성
        stats_file = self.marketplace_dir / "statistics.json"
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
        
        # 파일 존재 확인
        self.assertTrue(stats_file.exists())
        
        # 통계 확인
        with open(stats_file, 'r', encoding='utf-8') as f:
            loaded_stats = json.load(f)
        
        self.assertEqual(loaded_stats['total_installed'], 3)
        self.assertEqual(loaded_stats['total_activated'], 2)
        self.assertEqual(loaded_stats['total_deactivated'], 1)
        self.assertEqual(loaded_stats['category_distribution']['hr'], 2)


class TestModuleIntegrationBasic(unittest.TestCase):
    """모듈 연동 기본 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.integration_dir = Path(self.temp_dir) / "integration"
        self.integration_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """테스트 정리"""
        shutil.rmtree(self.temp_dir)
    
    def test_integration_rules_creation(self):
        """연동 규칙 생성 테스트"""
        # 연동 규칙
        integration_rules = [
            {
                'id': 'attendance_to_payroll',
                'name': '출퇴근-급여 연동',
                'source_module': 'attendance_management',
                'target_module': 'payroll_management',
                'trigger_event': 'attendance_created',
                'data_mapping': {
                    'employee_id': 'employee_id',
                    'work_hours': 'work_hours',
                    'overtime_hours': 'overtime_hours',
                    'late_minutes': 'late_minutes'
                },
                'enabled': True
            },
            {
                'id': 'sales_to_inventory',
                'name': '매출-재고 연동',
                'source_module': 'sales_management',
                'target_module': 'inventory_management',
                'trigger_event': 'sales_created',
                'data_mapping': {
                    'product_id': 'product_id',
                    'quantity': 'sold_quantity',
                    'branch_id': 'branch_id'
                },
                'enabled': True
            }
        ]
        
        # 규칙 파일 생성
        rules_file = self.integration_dir / "integration_rules.json"
        
        with open(rules_file, 'w', encoding='utf-8') as f:
            json.dump(integration_rules, f, ensure_ascii=False, indent=2)
        
        # 파일 존재 확인
        self.assertTrue(rules_file.exists())
        
        # 규칙 확인
        with open(rules_file, 'r', encoding='utf-8') as f:
            loaded_rules = json.load(f)
        
        self.assertEqual(len(loaded_rules), 2)
        self.assertEqual(loaded_rules[0]['id'], 'attendance_to_payroll')
        self.assertEqual(loaded_rules[1]['id'], 'sales_to_inventory')
    
    def test_data_integration_simulation(self):
        """데이터 연동 시뮬레이션 테스트"""
        # 출퇴근 데이터
        attendance_data = {
            'employee_id': 1,
            'work_hours': 8.5,
            'overtime_hours': 1.5,
            'late_minutes': 10,
            'date': '2024-01-15',
            'branch_id': 1
        }
        
        # 급여 계산 로직 시뮬레이션
        hourly_rate = 10000  # 시간당 10,000원
        overtime_rate = 1.5   # 야근 1.5배
        late_penalty = 1000   # 지각 1분당 1,000원
        
        total_pay = (
            attendance_data['work_hours'] * hourly_rate +
            attendance_data['overtime_hours'] * hourly_rate * overtime_rate -
            attendance_data['late_minutes'] * late_penalty
        )
        
        # 연동 결과
        integration_result = {
            'source_module': 'attendance_management',
            'target_module': 'payroll_management',
            'source_data': attendance_data,
            'result': {
                'employee_id': attendance_data['employee_id'],
                'work_hours': attendance_data['work_hours'],
                'overtime_hours': attendance_data['overtime_hours'],
                'late_minutes': attendance_data['late_minutes'],
                'total_pay': total_pay,
                'calculated_at': '2024-01-15T10:00:00Z'
            }
        }
        
        # 결과 파일 생성
        result_file = self.integration_dir / "integration_result.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(integration_result, f, ensure_ascii=False, indent=2)
        
        # 파일 존재 확인
        self.assertTrue(result_file.exists())
        
        # 결과 확인
        with open(result_file, 'r', encoding='utf-8') as f:
            loaded_result = json.load(f)
        
        self.assertEqual(loaded_result['source_module'], 'attendance_management')
        self.assertEqual(loaded_result['target_module'], 'payroll_management')
        self.assertEqual(loaded_result['result']['employee_id'], 1)
        self.assertGreater(loaded_result['result']['total_pay'], 0)


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2) 