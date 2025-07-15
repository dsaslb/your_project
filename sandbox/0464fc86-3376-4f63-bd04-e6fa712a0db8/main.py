#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고객 피드백 시스템 모듈
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    return jsonify({'message': 'Hello from 고객 피드백 시스템!'})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
