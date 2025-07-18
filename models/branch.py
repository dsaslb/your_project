from datetime import datetime


class Branch:
    def __init__(self, id, name, parent_id=None, is_head_office=False):
        self.id = id
        self.name = name
        self.parent_id = parent_id  # None이면 본사
        self.is_head_office = is_head_office
        self.policies = []  # 일괄 적용 정책
        self.reports = []  # 일괄 적용 리포트
        self.created_at = datetime.now()

    def apply_policy(self, policy):
        self.policies.append(policy)

    def apply_report(self, report):
        self.reports.append(report)
