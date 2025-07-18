# -*- coding: utf-8 -*-
"""
기본 테스트 파일
TestConfig 설정이 정상적으로 작동하는지 확인
"""

import pytest
from flask import Flask
from config import TestConfig


def test_config_import():
    """TestConfig가 정상적으로 import되는지 테스트"""
    assert TestConfig is not None
    assert hasattr(TestConfig, 'TESTING')
    assert TestConfig.TESTING is True


def test_config_database_uri():
    """TestConfig의 데이터베이스 URI가 메모리 데이터베이스로 설정되는지 테스트"""
    assert TestConfig.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"


def test_config_secret_key():
    """TestConfig의 SECRET_KEY가 설정되는지 테스트"""
    assert TestConfig.SECRET_KEY == "test-secret"


def test_config_csrf_disabled():
    """TestConfig에서 CSRF가 비활성화되는지 테스트"""
    assert TestConfig.WTF_CSRF_ENABLED is False


def test_app_creation():
    """Flask 앱이 TestConfig로 정상 생성되는지 테스트"""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///:memory:"
    assert app.config['SECRET_KEY'] == "test-secret"
    assert app.config['WTF_CSRF_ENABLED'] is False


if __name__ == "__main__":
    pytest.main([__file__]) 