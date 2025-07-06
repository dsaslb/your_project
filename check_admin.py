from app import app
from models import User, db

with app.app_context():
    # 관리자 계정 확인
    admin = User.query.filter_by(username="admin").first()

    if admin:
        print(f"✅ 관리자 계정 존재: {admin.username}")
        print(f"   역할: {admin.role}")
        print(f"   상태: {admin.status}")
        print(f"   이메일: {admin.email}")
        
        # 비밀번호 재설정
        print("\n🔄 관리자 비밀번호를 'admin123'으로 재설정합니다...")
        admin.set_password("admin123")
        db.session.commit()
        print("✅ 비밀번호가 성공적으로 재설정되었습니다!")
        print("   사용자명: admin")
        print("   비밀번호: admin123")
        
    else:
        print("❌ 관리자 계정이 없습니다.")

        # 새 관리자 계정 생성
        admin = User(
            username="admin",
            email="admin@restaurant.com",
            role="admin",
            status="approved",
        )
        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("✅ 새 관리자 계정을 생성했습니다.")
        print("   사용자명: admin")
        print("   비밀번호: admin123")

    # 전체 사용자 수 확인
    total_users = User.query.count()
    print(f"\n📊 전체 사용자 수: {total_users}")
    
    print("\n🔐 로그인 정보:")
    print("   URL: http://localhost:5000/auth/login")
    print("   아이디: admin")
    print("   비밀번호: admin123")
