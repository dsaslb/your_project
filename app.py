from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, time
from sqlalchemy import func, extract
from sqlalchemy.sql import text
import os
import json
import csv
import io
from functools import wraps
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import traceback
from werkzeug.utils import secure_filename
import zipfile
import shutil
import re
from io import StringIO
from markupsafe import escape as escape_html

from extensions import db, login_manager, limiter, cache, csrf, init_extensions
from config import DevConfig

app = Flask(__name__)
app.config.from_object(DevConfig)

# 확장 기능 초기화
init_extensions(app)
migrate = Migrate(app, db)

# 모델 import (순환 import 방지)
from models import User, Attendance, Notice, NoticeComment, NoticeHistory, CommentHistory, Report, NoticeRead, ApproveLog, ShiftRequest, Notification, Suggestion, Feedback, ActionLog

# 유틸리티 함수 import
from utils.logger import log_action, log_error, log_security_event
from utils.decorators import admin_required
from utils.security import sanitize_input, hash_sensitive_data
from utils.file_utils import delete_file, backup_files, restore_files
from utils.email_utils import send_email

# --- 블루프린트 등록 ---
from routes.notice import notice_bp
app.register_blueprint(notice_bp)

# --- API 블루프린트 등록 ---
from api.auth import api_auth_bp
from api.notice import api_notice_bp
from api.comment import api_comment_bp
from api.report import api_report_bp
from api.admin_report import admin_report_bp
from api.comment_report import comment_report_bp
from api.admin_log import admin_log_bp
from api.admin_report_stat import admin_report_stat_bp

app.register_blueprint(api_auth_bp)
app.register_blueprint(api_notice_bp)
app.register_blueprint(api_comment_bp)
app.register_blueprint(api_report_bp)
app.register_blueprint(admin_report_bp)
app.register_blueprint(comment_report_bp)
app.register_blueprint(admin_log_bp)
app.register_blueprint(admin_report_stat_bp)

# ... (기존의 다른 모든 라우트 함수들은 여기에 위치합니다)

if __name__ == '__main__':
    app.run(debug=True)
