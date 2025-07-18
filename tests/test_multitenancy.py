import unittest
import json
import uuid
from app import app, db
from models_main import Industry, Brand, Branch, User, IndustryPlugin, PluginAccessControl

class MultitenancyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.create_test_data()

    def create_test_data(self):
        unique = str(uuid.uuid4())[:8]
        # 테스트용 업종 생성
        industry = Industry(name=f"테스트 레스토랑_{unique}", code=f"TEST_RESTAURANT_{unique}", description="테스트용 음식점 업종")
        db.session.add(industry)
        db.session.commit()
        self.industry_id = industry.id

        # 테스트용 브랜드 생성
        brand = Brand(name=f"테스트 브랜드_{unique}", code=f"TEST_BRAND_{unique}", industry_id=industry.id, description="테스트용 브랜드")
        db.session.add(brand)
        db.session.commit()
        self.brand_id = brand.id

        # 테스트용 매장 생성
        branch = Branch(name=f"테스트 매장_{unique}", brand_id=brand.id, address="테스트 주소")
        db.session.add(branch)
        db.session.commit()
        self.branch_id = branch.id

        # 테스트용 사용자 생성
        user = User(username=f"testuser_{unique}", email=f"test{unique}@test.com", role="staff", branch_id=branch.id)
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        # 테스트용 플러그인 생성
        plugin = IndustryPlugin(name="출근 관리", code=f"PLUGIN_ATTENDANCE_{unique}", description="직원 출근 관리", is_active=True, industry_id=industry.id)
        db.session.add(plugin)
        db.session.commit()
        self.plugin_id = plugin.id

    def test_industry_crud(self):
        """업종 CRUD 테스트"""
        # 업종 목록 조회
        response = self.app.get('/api/industries')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('industries', data)

        # 업종 생성
        unique = str(uuid.uuid4())[:8]
        new_industry = {'name': '카페', 'code': f'CAFE_{unique}', 'description': '카페 업종'}
        response = self.app.post('/api/industries', json=new_industry)
        self.assertEqual(response.status_code, 201)

    def test_brand_crud(self):
        """브랜드 CRUD 테스트"""
        # 브랜드 목록 조회
        response = self.app.get('/api/brands')
        self.assertEqual(response.status_code, 200)

        # 브랜드 생성
        unique = str(uuid.uuid4())[:8]
        new_brand = {'name': '새 브랜드', 'code': f'NEW_BRAND_{unique}', 'industry_id': self.industry_id, 'description': '새 브랜드'}
        response = self.app.post('/api/brands', json=new_brand)
        self.assertEqual(response.status_code, 201)

    def test_branch_crud(self):
        """매장 CRUD 테스트"""
        # 매장 목록 조회
        response = self.app.get('/api/branches')
        self.assertEqual(response.status_code, 200)

        # 매장 생성
        new_branch = {'name': '새 매장', 'brand_id': self.brand_id, 'address': '새 주소'}
        response = self.app.post('/api/branches', json=new_branch)
        self.assertEqual(response.status_code, 201)

    def test_user_crud(self):
        """사용자 CRUD 테스트"""
        # 사용자 목록 조회
        response = self.app.get('/api/users')
        self.assertEqual(response.status_code, 200)

        # 사용자 생성
        new_user = {'username': 'newuser', 'email': 'new@test.com', 'role': 'staff', 'branch_id': self.branch_id}
        response = self.app.post('/api/users', json=new_user)
        self.assertEqual(response.status_code, 201)

    def test_plugin_access_control(self):
        """플러그인 접근 제어 테스트"""
        # 브랜드별 플러그인 접근 권한 설정
        access_data = {
            'brand_id': self.brand_id,
            'is_allowed': True,
            'access_type': 'use'
        }
        response = self.app.post(f'/api/plugins/{self.plugin_id}/access-control/brand', json=access_data)
        self.assertEqual(response.status_code, 200)

        # 매장별 플러그인 접근 권한 설정
        access_data = {
            'branch_id': self.branch_id,
            'is_allowed': True,
            'access_type': 'use'
        }
        response = self.app.post(f'/api/plugins/{self.plugin_id}/access-control/branch', json=access_data)
        self.assertEqual(response.status_code, 200)

    def test_plugin_functionality(self):
        """플러그인 기능 테스트"""
        # 출근 관리 플러그인 테스트
        response = self.app.post('/api/plugins/attendance/check-in')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

        # 재고 관리 플러그인 테스트
        response = self.app.get('/api/plugins/inventory/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main() 