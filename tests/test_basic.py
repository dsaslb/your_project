# -*- coding: utf-8 -*-
"""
기본 테스트 파일
TestConfig 설정이 정상적으로 작동하는지 확인
"""

import pytest
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import_app():
    """애플리케이션 모듈이 정상적으로 import되는지 테스트"""
    try:
        import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import app: {e}")

def test_import_models():
    """모델 모듈들이 정상적으로 import되는지 테스트"""
    try:
        from models_main import User, Brand, Branch, Industry
        assert User is not None
        assert Brand is not None
        assert Branch is not None
        assert Industry is not None
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")

def test_import_plugin_models():
    """플러그인 모델들이 정상적으로 import되는지 테스트"""
    try:
        from models.plugin_models import Plugin, PluginInstallation, PluginReview
        assert Plugin is not None
        assert PluginInstallation is not None
        assert PluginReview is not None
    except ImportError as e:
        pytest.fail(f"Failed to import plugin models: {e}")

def test_basic_math():
    """기본 수학 연산 테스트"""
    assert 2 + 2 == 4
    assert 3 * 4 == 12
    assert 10 / 2 == 5

def test_string_operations():
    """문자열 연산 테스트"""
    test_string = "Hello, World!"
    assert len(test_string) == 13
    assert test_string.upper() == "HELLO, WORLD!"
    assert test_string.lower() == "hello, world!"

def test_list_operations():
    """리스트 연산 테스트"""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert sum(test_list) == 15
    assert test_list[0] == 1
    assert test_list[-1] == 5

def test_dict_operations():
    """딕셔너리 연산 테스트"""
    test_dict = {"name": "Test", "value": 42}
    assert len(test_dict) == 2
    assert test_dict["name"] == "Test"
    assert test_dict["value"] == 42
    assert "name" in test_dict
    assert "missing" not in test_dict

if __name__ == "__main__":
    pytest.main([__file__]) 