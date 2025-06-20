import pytest
from app import app as flask_app
from models import db, User, Notice
from config import TestConfig

@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    flask_app.config.from_object(TestConfig)
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    """Creates a new database session for a test, and rolls back changes after."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.begin_nested()

        @db.event.listens_for(db.session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()
        
        yield db.session
        
        db.session.remove()
        transaction.rollback()
        connection.close()

@pytest.fixture()
def admin_user(session):
    """Fixture for a test admin user."""
    user = User(username='testadmin', email='admin@example.com', role='admin', status='approved')
    user.set_password('a-very-secure-admin-password-123')
    session.add(user)
    session.commit()
    return user

@pytest.fixture()
def notice(session, admin_user):
    """Fixture for a sample notice."""
    n = Notice(title="Original Title", content="Original Content", author_id=admin_user.id, category="공지사항")
    session.add(n)
    session.commit()
    return n 