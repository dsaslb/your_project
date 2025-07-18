# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 기본 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# CORS 설정
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'running',
        'message': '서버가 정상적으로 실행 중입니다.'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting simple app server on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000) 