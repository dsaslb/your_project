# import pytest  # 사용되지 않으므로 삭제

# from models import Notice, NoticeHistory, User, db  # 사용되지 않으므로 삭제
from services.notice_service import update_notice


def test_update_notice(session, notice, admin_user):
    """
    GIVEN a notice object and new data
    WHEN the update_notice service is called
    THEN check the notice object is correctly updated
    """
    # Data to be updated
    title = "Updated Title"
    content = "Updated Content"
    category = "자료실"

    # Call the service function
    updated_notice = update_notice(notice.id, title, content, category)

    # Assertions for the notice object
    assert updated_notice is not None
    assert updated_notice.title == "Updated Title"
    assert updated_notice.content == "Updated Content"
    assert updated_notice.category == "자료실"
