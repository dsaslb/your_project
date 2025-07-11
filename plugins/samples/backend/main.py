"""
샘플 플러그인
플러그인 개발 샘플 템플릿
"""
from flask import Blueprint
from core.backend.plugin_interface import BasePlugin, PluginMetadata

class SamplePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint('samples', __name__)
        self.metadata = PluginMetadata(
            name="샘플 플러그인",
            version="1.0.0",
            description="플러그인 개발 샘플 템플릿",
            author="Your Program Team",
            category="general",
            dependencies=[],
            permissions=["sample_access"],
            enabled=True
        )
    def initialize(self) -> bool:
        self._initialized = True
        return True
    def cleanup(self) -> bool:
        self._initialized = False
        return True
    def get_metadata(self):
        return self.metadata

def create_plugin() -> SamplePlugin:
    return SamplePlugin() 