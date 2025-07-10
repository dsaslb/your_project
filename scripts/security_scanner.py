import os
import json
import hashlib
from datetime import datetime

def scan_security_issues():
    """蹂댁븞 ?댁뒋 ?ㅼ틪"""
    issues = []
    
    # 1. ?섍꼍 蹂???뚯씪 泥댄겕
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'SECRET_KEY' in content and 'test' in content.lower():
                issues.append("WARNING: Default SECRET_KEY detected in .env")
            if 'password' in content.lower() and 'admin' in content.lower():
                issues.append("WARNING: Default password detected in .env")
    
    # 2. ?곗씠?곕쿋?댁뒪 ?뚯씪 沅뚰븳 泥댄겕
    db_path = "instance/your_program.db"
    if os.path.exists(db_path):
        # Windows?먯꽌???뚯씪 沅뚰븳 泥댄겕媛 ?ㅻ쫫
        try:
            import stat
            mode = os.stat(db_path).st_mode
            if mode & stat.S_IROTH:  # ?ㅻⅨ ?ъ슜???쎄린 沅뚰븳
                issues.append("WARNING: Database file has public read permissions")
        except:
            pass
    
    # 3. 濡쒓렇 ?뚯씪 泥댄겕
    log_files = []
    for root, dirs, files in os.walk('logs'):
        for file in files:
            if file.endswith('.log'):
                log_files.append(os.path.join(root, file))
    
    if len(log_files) > 10:
        issues.append(f"INFO: {len(log_files)} log files found - consider log rotation")
    
    # 4. ?꾩떆 ?뚯씪 泥댄겕
    temp_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.startswith('temp_') or file.endswith('.tmp'):
                temp_files.append(os.path.join(root, file))
    
    if temp_files:
        issues.append(f"INFO: {len(temp_files)} temporary files found")
    
    # 5. Git 蹂댁븞 泥댄겕
    if os.path.exists('.git'):
        gitignore_path = '.gitignore'
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                content = f.read()
                if '.env' not in content:
                    issues.append("WARNING: .env file not in .gitignore")
                if '*.db' not in content:
                    issues.append("WARNING: Database files not in .gitignore")
    
    return issues

def generate_security_report():
    """蹂댁븞 由ы룷???앹꽦"""
    issues = scan_security_issues()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(issues),
        "issues": issues,
        "recommendations": [
            "Change default passwords",
            "Use strong SECRET_KEY",
            "Enable HTTPS in production",
            "Regular security updates",
            "Monitor access logs"
        ]
    }
    
    # 由ы룷?????
    with open("logs/security/security_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    report = generate_security_report()
    print(json.dumps(report, indent=2))
