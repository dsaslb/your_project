from models import Notice, NoticeHistory, db


def update_notice(notice_id, data, file, editor_id):
    """
    공지사항을 수정하고 이력을 기록합니다.
    :param notice_id: 수정할 공지사항 ID
    :param data: 수정할 데이터 (dict)
    :param file: 업로드된 파일 객체
    :param editor_id: 수정자 ID
    :return: 수정된 Notice 객체 또는 None
    """
    notice = Notice.query.get(notice_id)
    if not notice:
        return None

    # 1. 변경 이력 저장
    history = NoticeHistory(
        notice_id=notice.id,
        editor_id=editor_id,
        before_title=notice.title,
        before_content=notice.content,
        before_file_path=notice.file_path,
        before_file_type=notice.file_type,
        action="edit",
    )
    db.session.add(history)

    # 2. 실제 데이터 수정
    notice.title = data.get("title", notice.title)
    notice.content = data.get("content", notice.content)
    notice.category = data.get("category", notice.category)

    # 3. 파일 처리
    if file and file.filename != "":
        from utils.file_utils import delete_file, save_file

        # 기존 파일 삭제
        if notice.file_path:
            delete_file(notice.file_path)

        # 새 파일 저장
        file_path, file_type = save_file(file)
        notice.file_path = file_path
        notice.file_type = file_type

    db.session.commit()

    return notice
