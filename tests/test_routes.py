from models import Notice, NoticeHistory

def test_edit_notice_route(client, session, admin_user, notice):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/notice/<id>/edit' route is requested via POST by an authenticated admin
    THEN check that the response is valid and the notice is updated in the database
    """
    # 1. Log in the admin user
    with client.session_transaction() as sess:
        sess['_user_id'] = admin_user.id
        sess['_fresh'] = True

    # 2. Prepare form data and send POST request
    form_data = {
        'title': 'Route Updated Title',
        'content': 'Route Updated Content',
        'category': '행사안내'
    }
    url = f'/notice/{notice.id}/edit'
    response = client.post(url, data=form_data, follow_redirects=True)
    
    # 3. Assert response
    assert response.status_code == 200
    assert "공지사항이 성공적으로 수정되었습니다.".encode("utf-8") in response.data
    
    # 4. Assert database changes for the notice
    updated_notice = session.get(Notice, notice.id)
    assert updated_notice.title == 'Route Updated Title'
    assert updated_notice.content == 'Route Updated Content'

    # 5. Assert database changes for the history
    history = NoticeHistory.query.filter_by(notice_id=notice.id).order_by(NoticeHistory.edited_at.desc()).first()
    assert history is not None
    assert history.before_title == "Original Title" # Check if history recorded the state before this update
    assert history.editor_id == admin_user.id 