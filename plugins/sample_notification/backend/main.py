"""
샘플 알림 플러그인
알림 기능 샘플
"""
from flask import Blueprint
from core.backend.plugin_interface import BasePlugin, PluginMetadata

class SampleNotificationPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.blueprint = Blueprint('sample_notification', __name__)
        self.metadata = PluginMetadata(
            name="샘플 알림",
            version="1.0.0",
            description="알림 기능 샘플",
            author="Your Program Team",
            category="general",
            dependencies=[],
            permissions=["notification_access"],
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

def create_plugin() -> SampleNotificationPlugin:
    return SampleNotificationPlugin() 