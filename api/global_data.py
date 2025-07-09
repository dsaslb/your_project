from flask import Blueprint, jsonify

# 계층형 데이터 더미 예시
DUMMY_DATA = {
    "industries": [
        {
            "id": "hospital",
            "name": "병원",
            "brands": [
                {
                    "id": "brand1",
                    "name": "서울메디컬",
                    "stores": [
                        {
                            "id": "store1",
                            "name": "강남점",
                            "staff": [
                                {"id": "s1", "name": "김의사", "role": "의사"},
                                {"id": "s2", "name": "이간호사", "role": "간호사"}
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "beauty",
            "name": "미용실",
            "brands": [
                {
                    "id": "brand2",
                    "name": "헤어아트",
                    "stores": [
                        {
                            "id": "store2",
                            "name": "홍대점",
                            "staff": [
                                {"id": "s3", "name": "박디자이너", "role": "디자이너"},
                                {"id": "s4", "name": "최스텝", "role": "스텝"}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

global_data_bp = Blueprint('global_data', __name__)

@global_data_bp.route('/api/global-data', methods=['GET'])
def get_global_data():
    return jsonify({"success": True, "data": DUMMY_DATA}) 