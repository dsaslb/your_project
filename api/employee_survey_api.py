from flask import Blueprint, jsonify
from models.employee_survey import EmployeeSurvey
from sqlalchemy import func
from extensions import db

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('/api/survey/summary', methods=['GET'])
def survey_summary():
    avg_score = db.session.query(func.avg(EmployeeSurvey.score)).scalar()
    if avg_score is None:
        avg_score = 0
    if avg_score < 3.0:
        recommendation = "건강검진/휴식/복지포인트 지급 추천"
    else:
        recommendation = "우수 직원 보상/포인트 지급"
    return jsonify({'avg_score': avg_score, 'recommendation': recommendation}) 