from flask import jsonify

@app.route('/api/admin/dashboard-stats')
def get_dashboard_stats():
    # 예시: 승인률, 처리속도, 피드백 수, 차트 데이터 등
    stats = {
        'approval_rate': 92,
        'avg_process_time': 13,
        'feedback_count': 27,
        'chart_labels': ['월', '화', '수', '목', '금', '토', '일'],
        'approval_counts': [5, 7, 8, 6, 9, 4, 3],
        'feedback_counts': [1, 2, 3, 2, 4, 1, 1],
    }
    return jsonify({'success': True, 'stats': stats}) 