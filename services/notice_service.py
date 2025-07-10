from models import Notice, db
from datetime import datetime


def update_notice(notice_id, title, content, category=None):
    """공지사항 수정"""
    notice = Notice.query.filter_by(id=notice_id).first()
    if notice:
        notice.title = title
        notice.content = content
        if category:
            notice.category = category
        notice.updated_at = datetime.utcnow()
        db.session.commit()
        return notice
    return None

def create_notice_for_event(title, content, type, priority, author_id, target_audience=None, category=None):
    """
    타 업무(스케줄/발주/재고 등)에서 호출하는 공통 알림/공지 등록 함수
    :param title: 알림/공지 제목
    :param content: 알림/공지 내용
    :param type: 'notice' | 'alert' | 'info' 등
    :param priority: 'high' | 'medium' | 'low'
    :param author_id: 작성자(시스템/관리자 등)
    :param target_audience: 대상(전체/주방/홀 등, 옵션)
    :param category: 카테고리(발주/스케줄/재고 등, 옵션)
    :return: 생성된 Notice 객체
    """
    notice = Notice()
    notice.title = title
    notice.content = content
    notice.category = category
    notice.author_id = author_id
    # type, priority, target_audience 등은 Notice 모델에 따라 커스텀 필드로 추가 필요시 확장
    db.session.add(notice)
    db.session.commit()
    return notice
