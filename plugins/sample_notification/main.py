"""
샘플 알림 플러그인
"""

class SamplenotificationPlugin:
    def __init__(self):
        self.name = "sample_notification"
        self.version = "1.0.0"
        self.author = "System"
        self.description = "샘플 알림 플러그인"
    
    def initialize(self):
        """플러그인 초기화"""
        print(f"{self.name} 플러그인 초기화")
    
    def get_routes(self):
        """라우트 정보 반환"""
        return []
    
    def get_menu_items(self):
        """메뉴 아이템 반환"""
        return []

# 플러그인 인스턴스
plugin = SamplenotificationPlugin()
