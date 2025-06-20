import pytest
from models import Notice, User, db, NoticeHistory
from services.notice_service import update_notice

def test_update_notice(session, notice, admin_user):
    """
    GIVEN a notice object and new data
    WHEN the update_notice service is called
    THEN check the notice object and its history are correctly updated
    """
    # Data to be updated
    update_data = {
        'title': 'Updated Title',
        'content': 'Updated Content',
        'category': '자료실'
    }
    
    # Call the service function
    updated_notice = update_notice(notice.id, update_data, None, admin_user.id)
    
    # Assertions for the notice object
    assert updated_notice is not None
    assert updated_notice.title == "Updated Title"
    assert updated_notice.content == "Updated Content"
    assert updated_notice.category == "자료실"
    
    # Assertions for the history record
    history = NoticeHistory.query.filter_by(notice_id=notice.id).order_by(NoticeHistory.edited_at.desc()).first()
    assert history is not None
    assert history.before_title == "Original Title"
    assert history.before_content == "Original Content"
    assert history.editor_id == admin_user.id 