from models_main import Notice, db
from api.utils import token_required  # pyright: ignore
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore


api_notice_bp = Blueprint("api_notice", __name__, url_prefix="/api/notices")


@api_notice_bp.route("/", methods=["GET"])
def get_notices():
    """
    공지사항 목록 조회
    ---
    tags:
      - Notice
    summary: 공개된 공지사항 목록을 조회합니다
    description: 숨김 처리되지 않은 공지사항들을 최신순으로 조회합니다.
    parameters:
      - name: page
        in: query
        type: integer
        description: 페이지 번호 (기본값: 1)
        required: false
        default: 1
      - name: per_page
        in: query
        type: integer
        description: 페이지당 항목 수 (기본값: 20)
        required: false
        default: 20
    responses:
      200:
        description: 공지사항 목록 조회 성공
        schema:
          type: object
          properties:
            notices:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: 공지사항 ID
                  title:
                    type: string
                    description: 공지사항 제목
                  author:
                    type: string
                    description: 작성자명
                  created_at:
                    type: string
                    format: date-time
                    description: 작성일시
            total:
              type: integer
              description: 전체 공지사항 수
            page:
              type: integer
              description: 현재 페이지 번호
            pages:
              type: integer
              description: 전체 페이지 수
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = (
        Notice.query.filter_by(is_hidden=False)
        .order_by(Notice.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    notices = pagination.items
    output = []
    for notice in notices:
        notice_data = {
            "id": notice.id,
            "title": notice.title,
            "author": notice.author.username,
            "created_at": notice.created_at.isoformat(),
        }
        output.append(notice_data)

    return jsonify(
        {
            "notices": output,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }
    )


@api_notice_bp.route("/", methods=["POST"])
@token_required
def create_notice(current_user):
    """
    공지사항 등록
    ---
    tags:
      - Notice
    summary: 새로운 공지사항을 등록합니다
    description: 관리자 권한이 필요하며, JWT 토큰 인증이 필요합니다.
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - content
          properties:
            title:
              type: string
              description: 공지사항 제목
              example: "중요 공지사항"
            content:
              type: string
              description: 공지사항 내용
              example: "이번 주 회의 일정 변경 안내입니다."
            category:
              type: string
              description: 공지사항 카테고리
              example: "공지사항"
              enum: ["공지사항", "자료실", "행사안내", "기타"]
    responses:
      201:
        description: 공지사항 등록 성공
        schema:
          type: object
          properties:
            message:
              type: string
              example: "New notice created!"
            notice_id:
              type: integer
              description: 생성된 공지사항 ID
              example: 123
      400:
        description: 잘못된 요청
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Title and content are required"
      401:
        description: 인증 필요
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token is missing!"
    """
    data = request.json
    if not data or not data.get("title") or not data.get("content"):
        return jsonify({"msg": "Title and content are required"}), 400

    new_notice = Notice(
        title=data["title"],
        content=data["content"],
        author_id=current_user.id,
        category=data.get("category", "공지사항"),
    )
    db.session.add(new_notice)
    db.session.commit()
    return jsonify({"message": "New notice created!", "notice_id": new_notice.id}), 201
