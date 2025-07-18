"""
모듈 마켓플레이스 시스템 통합 테스트
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest  # async 테스트 지원
import asyncio

# 테스트 대상 모듈들
from core.backend.module_marketplace_system import (
    ModuleMarketplaceSystem,
    ModuleScope,
    ModuleStatus,
)
from core.backend.module_integration_system import (
    ModuleIntegrationSystem,
    IntegrationType,
    DataSource,
)


class TestModuleMarketplaceSystem(unittest.TestCase):
    """모듈 마켓플레이스 시스템 테스트"""

    def setUp(self):
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.marketplace_dir = Path(self.temp_dir) / "marketplace"
        self.modules_dir = Path(self.temp_dir) / "plugins"

        # 시스템 인스턴스 생성
        self.marketplace_system = ModuleMarketplaceSystem(
            marketplace_dir=str(self.marketplace_dir), modules_dir=str(self.modules_dir)
        )

        # 테스트 사용자 ID
        self.test_user_id = 1
        self.test_scope_id = 1

    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir)

    def test_marketplace_initialization(self):
        """마켓플레이스 초기화 테스트"""
        # 기본 디렉토리 생성 확인
        self.assertTrue(self.marketplace_dir.exists())
        self.assertTrue(self.modules_dir.exists())

        # 하위 디렉토리 생성 확인
        self.assertTrue((self.marketplace_dir / "modules").exists())
        self.assertTrue((self.marketplace_dir / "installed").exists())
        self.assertTrue((self.marketplace_dir / "configs").exists())
        self.assertTrue((self.marketplace_dir / "backups").exists())

        # 기본 모듈 목록 확인
        modules = self.marketplace_system.get_available_modules()
        self.assertGreater(len(modules), 0)

        # 출퇴근 관리 모듈 존재 확인
        attendance_module = next(
            (m for m in modules if m["id"] == "attendance_management"), None
        )
        self.assertIsNotNone(attendance_module)
        self.assertEqual(attendance_module["name"], "출퇴근 관리")

    def test_module_installation(self):
        """모듈 설치 테스트"""
        # 출퇴근 관리 모듈 설치
        success = self.marketplace_system.install_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        self.assertTrue(success)

        # 설치 상태 확인
        is_installed = self.marketplace_system.is_module_installed(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )
        self.assertTrue(is_installed)

        # 설치된 모듈 목록 확인
        installed_modules = self.marketplace_system.get_installed_modules(
            self.test_user_id, self.test_scope_id, ModuleScope.BRANCH
        )
        self.assertEqual(len(installed_modules), 1)
        self.assertEqual(installed_modules[0]["id"], "attendance_management")

    def test_module_activation(self):
        """모듈 활성화 테스트"""
        # 모듈 설치
        self.marketplace_system.install_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        # 모듈 활성화
        success = self.marketplace_system.activate_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        self.assertTrue(success)

        # 활성화 상태 확인
        is_activated = self.marketplace_system.is_module_activated(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )
        self.assertTrue(is_activated)

    def test_module_deactivation(self):
        """모듈 비활성화 테스트"""
        # 모듈 설치 및 활성화
        self.marketplace_system.install_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )
        self.marketplace_system.activate_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        # 모듈 비활성화
        success = self.marketplace_system.deactivate_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        self.assertTrue(success)

        # 비활성화 상태 확인
        is_activated = self.marketplace_system.is_module_activated(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )
        self.assertFalse(is_activated)

    def test_module_uninstallation(self):
        """모듈 제거 테스트"""
        # 모듈 설치
        self.marketplace_system.install_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        # 모듈 제거
        success = self.marketplace_system.uninstall_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        self.assertTrue(success)

        # 제거 상태 확인
        is_installed = self.marketplace_system.is_module_installed(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )
        self.assertFalse(is_installed)

    def test_module_config_management(self):
        """모듈 설정 관리 테스트"""
        # 모듈 설치
        self.marketplace_system.install_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        # 설정 업데이트
        test_config = {
            "auto_notifications": True,
            "sync_interval": "realtime",
            "ai_analysis": True,
            "auto_backup": False,
        }

        success = self.marketplace_system.update_module_config(
            "attendance_management",
            self.test_user_id,
            test_config,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        self.assertTrue(success)

        # 설정 조회
        config = self.marketplace_system.get_module_config(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        self.assertIsNotNone(config)
        self.assertEqual(config["auto_notifications"], True)
        self.assertEqual(config["sync_interval"], "realtime")
        self.assertEqual(config["ai_analysis"], True)
        self.assertEqual(config["auto_backup"], False)

    def test_module_statistics(self):
        """모듈 통계 테스트"""
        # 여러 모듈 설치
        modules_to_install = [
            "attendance_management",
            "sales_management",
            "payroll_management",
        ]

        for module_id in modules_to_install:
            self.marketplace_system.install_module(
                module_id, self.test_user_id, self.test_scope_id, ModuleScope.BRANCH
            )

        # 일부 모듈 활성화
        self.marketplace_system.activate_module(
            "attendance_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )
        self.marketplace_system.activate_module(
            "sales_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        # 통계 조회
        stats = self.marketplace_system.get_module_statistics(self.test_user_id)

        self.assertIsNotNone(stats)
        self.assertEqual(stats["total_installed"], 3)
        self.assertEqual(stats["total_activated"], 2)
        self.assertEqual(stats["total_deactivated"], 1)

    def test_module_search_and_filter(self):
        """모듈 검색 및 필터링 테스트"""
        # 카테고리별 필터링
        hr_modules = self.marketplace_system.get_available_modules(category="hr")
        self.assertGreater(len(hr_modules), 0)

        for module in hr_modules:
            self.assertEqual(module["category"], "hr")

        # 검색 기능
        search_results = self.marketplace_system.get_available_modules(search="출퇴근")
        self.assertGreater(len(search_results), 0)

        for module in search_results:
            self.assertTrue(
                "출퇴근" in module["name"]
                or "출퇴근" in module["description"]
                or "출퇴근" in module.get("tags", [])
            )

    def test_scope_based_installation(self):
        """범위별 모듈 설치 테스트"""
        # 사용자별 설치
        self.marketplace_system.install_module(
            "attendance_management", self.test_user_id, scope_type=ModuleScope.USER
        )

        # 매장별 설치
        self.marketplace_system.install_module(
            "sales_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRANCH,
        )

        # 브랜드별 설치
        self.marketplace_system.install_module(
            "payroll_management",
            self.test_user_id,
            self.test_scope_id,
            ModuleScope.BRAND,
        )

        # 각 범위별 설치된 모듈 확인
        user_modules = self.marketplace_system.get_installed_modules(
            self.test_user_id, scope_type=ModuleScope.USER
        )
        self.assertEqual(len(user_modules), 1)
        self.assertEqual(user_modules[0]["id"], "attendance_management")

        branch_modules = self.marketplace_system.get_installed_modules(
            self.test_user_id, self.test_scope_id, ModuleScope.BRANCH
        )
        self.assertEqual(len(branch_modules), 1)
        self.assertEqual(branch_modules[0]["id"], "sales_management")

        brand_modules = self.marketplace_system.get_installed_modules(
            self.test_user_id, self.test_scope_id, ModuleScope.BRAND
        )
        self.assertEqual(len(brand_modules), 1)
        self.assertEqual(brand_modules[0]["id"], "payroll_management")


class TestModuleIntegrationSystem(unittest.TestCase):
    """모듈 연동 시스템 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.integration_system = ModuleIntegrationSystem()

    def test_integration_rules_initialization(self):
        """연동 규칙 초기화 테스트"""
        rules = self.integration_system.get_integration_rules()
        self.assertGreater(len(rules), 0)

        # 기본 연동 규칙 확인
        rule_ids = [rule.id for rule in rules]
        expected_rules = [
            "attendance_to_payroll",
            "attendance_to_sales_efficiency",
            "sales_to_inventory",
            "qsc_to_employee_evaluation",
            "payroll_to_sales_analysis",
        ]

        for expected_rule in expected_rules:
            self.assertIn(expected_rule, rule_ids)

    @pytest.mark.asyncio
    async def test_attendance_to_payroll_integration(self):
        """출퇴근-급여 연동 테스트"""
        # 출퇴근 데이터 생성
        attendance_data = {
            "employee_id": 1,
            "work_hours": 8.5,
            "overtime_hours": 1.5,
            "late_minutes": 10,
            "branch_id": 1,
        }
        # 연동 처리 (동기 방식으로 변경)
        results = await self.integration_system.process_data_integration(
            attendance_data, "attendance_management", "attendance_created"
        )
        assert results is not None  # noqa
        assert len(results) > 0  # noqa

        # 급여 계산 결과 확인
        payroll_result = next(
            (r for r in results if r["target_module"] == "payroll_management"), None
        )
        self.assertIsNotNone(payroll_result)

        payroll_data = payroll_result["result"]
        self.assertEqual(payroll_data["employee_id"], 1)
        self.assertEqual(payroll_data["work_hours"], 8.5)
        self.assertEqual(payroll_data["overtime_hours"], 1.5)
        self.assertEqual(payroll_data["late_minutes"], 10)
        self.assertGreater(payroll_data["total_pay"], 0)

    @pytest.mark.asyncio
    async def test_sales_to_inventory_integration(self):
        """매출-재고 연동 테스트"""
        # 매출 데이터 생성
        sales_data = {
            "product_id": 1,
            "quantity": 5,
            "branch_id": 1,
            "date": "2024-01-15",
        }
        # 연동 처리 (동기 방식으로 변경)
        results = await self.integration_system.process_data_integration(
            sales_data, "sales_management", "sales_created"
        )
        assert results is not None  # noqa
        assert len(results) > 0  # noqa

        # 재고 업데이트 결과 확인
        inventory_result = next(
            (r for r in results if r["target_module"] == "inventory_management"), None
        )
        self.assertIsNotNone(inventory_result)

        inventory_data = inventory_result["result"]
        self.assertEqual(inventory_data["product_id"], 1)
        self.assertEqual(inventory_data["sold_quantity"], 5)
        self.assertEqual(inventory_data["branch_id"], 1)
        self.assertLess(inventory_data["current_stock"], 100)  # 초기 재고 100에서 감소

    @pytest.mark.asyncio
    async def test_qsc_to_employee_evaluation_integration(self):
        """QSC-직원 평가 연동 테스트"""
        # QSC 평가 데이터 생성
        qsc_data = {
            "employee_id": 1,
            "qsc_score": 85,
            "branch_id": 1,
            "evaluation_date": "2024-01-15",
        }
        # 연동 처리 (동기 방식으로 변경)
        results = await self.integration_system.process_data_integration(
            qsc_data, "qsc_management", "qsc_evaluated"
        )
        assert results is not None  # noqa
        assert len(results) > 0  # noqa

        # 직원 성과 업데이트 결과 확인
        employee_result = next(
            (r for r in results if r["target_module"] == "employee_management"), None
        )
        self.assertIsNotNone(employee_result)

        employee_data = employee_result["result"]
        self.assertEqual(employee_data["employee_id"], 1)
        self.assertEqual(employee_data["performance_score"], 85)
        self.assertEqual(employee_data["performance_grade"], "B")  # 85점은 B등급

    def test_integration_statistics(self):
        """연동 통계 테스트"""
        stats = self.integration_system.get_integration_statistics()

        self.assertIsNotNone(stats)
        self.assertIn("total_rules", stats)
        self.assertIn("enabled_rules", stats)
        self.assertIn("disabled_rules", stats)
        self.assertIn("rule_types", stats)
        self.assertIn("cache_size", stats)
        self.assertIn("last_sync_times", stats)

        self.assertGreater(stats["total_rules"], 0)
        self.assertGreaterEqual(stats["enabled_rules"], 0)
        self.assertGreaterEqual(stats["disabled_rules"], 0)

    def test_integration_health(self):
        """연동 상태 확인 테스트"""
        health = self.integration_system.get_integration_health()

        self.assertIsNotNone(health)
        self.assertIn("overall_status", health)
        self.assertIn("issues", health)
        self.assertIn("last_check", health)

        self.assertIn(health["overall_status"], ["healthy", "warning", "error"])

    @pytest.mark.asyncio
    async def test_batch_integration(self):
        """배치 연동 테스트"""
        # 배치 연동 실행 (동기 방식으로 변경)
        batch_results = await self.integration_system.run_batch_integration()

        self.assertIsNotNone(batch_results)
        self.assertIn("batch_results", batch_results)
        self.assertIn("total_processed", batch_results)
        self.assertIn("success_count", batch_results)
        self.assertIn("error_count", batch_results)

        self.assertGreaterEqual(batch_results["total_processed"], 0)
        self.assertGreaterEqual(batch_results["success_count"], 0)
        self.assertGreaterEqual(batch_results["error_count"], 0)


class TestModuleMarketplaceAPI(unittest.TestCase):
    """모듈 마켓플레이스 API 테스트"""

    def setUp(self):
        """테스트 설정"""
        from app import app

        self.app = app.test_client()
        self.app.testing = True

    def test_get_available_modules(self):
        """사용 가능한 모듈 목록 조회 테스트"""
        response = self.app.get("/api/module-marketplace/modules")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("modules", data)
        self.assertIn("categories", data)
        self.assertIn("total", data)

        # 모듈 목록 확인
        modules = data["modules"]
        self.assertGreater(len(modules), 0)

        # 출퇴근 관리 모듈 존재 확인
        attendance_module = next(
            (m for m in modules if m["id"] == "attendance_management"), None
        )
        self.assertIsNotNone(attendance_module)

    def test_get_module_detail(self):
        """모듈 상세 정보 조회 테스트"""
        response = self.app.get("/api/module-marketplace/modules/attendance_management")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("module", data)

        module = data["module"]
        self.assertEqual(module["id"], "attendance_management")
        self.assertEqual(module["name"], "출퇴근 관리")
        self.assertIn("features", module)
        self.assertIn("reviews", module)

    def test_get_module_categories(self):
        """모듈 카테고리 목록 조회 테스트"""
        response = self.app.get("/api/module-marketplace/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("categories", data)

        categories = data["categories"]
        self.assertGreater(len(categories), 0)
        self.assertIn("hr", categories)  # 인사 카테고리 존재 확인

    def test_get_trending_modules(self):
        """인기 모듈 목록 조회 테스트"""
        response = self.app.get("/api/module-marketplace/trending")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("modules", data)

        modules = data["modules"]
        self.assertGreater(len(modules), 0)
        self.assertLessEqual(len(modules), 10)  # 최대 10개

    def test_get_module_reviews(self):
        """모듈 리뷰 목록 조회 테스트"""
        response = self.app.get(
            "/api/module-marketplace/modules/attendance_management/reviews"
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("reviews", data)

        reviews = data["reviews"]
        self.assertGreater(len(reviews), 0)

        # 리뷰 구조 확인
        review = reviews[0]
        self.assertIn("id", review)
        self.assertIn("user_name", review)
        self.assertIn("rating", review)
        self.assertIn("comment", review)
        self.assertIn("created_at", review)


if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)
