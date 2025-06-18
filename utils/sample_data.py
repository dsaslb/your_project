from restaurant_project.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

def create_sample_users():
    users = [
        User(username='admin01', password='adminpass', role='admin', status='approved'),
        User(username='manager01', password='managerpass', role='manager', status='approved'),
        User(username='employee01', password='employeepass', role='employee', status='approved'),
    ]
    db.session.add_all(users)
    db.session.commit()

import click
from flask.cli import with_appcontext

@click.command("create-sample-data")
@with_appcontext
def create_sample_data():
    create_sample_users()
    click.echo("샘플 유저 생성 완료")
    