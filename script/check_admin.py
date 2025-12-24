
import sys
import os

# Add the backend directory to sys.path so we can import from server
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'backend')))

from server import app, db, User
from werkzeug.security import check_password_hash

def check_admin():
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("Admin user NOT found!")
        else:
            print(f"Admin user found. ID: {user.id}, Username: {user.username}, Hash: {user.password_hash}")
            if check_password_hash(user.password_hash, 'admin123'):
                print("Password 'admin123' is CORRECT.")
            else:
                print("Password 'admin123' is INCORRECT.")

if __name__ == "__main__":
    check_admin()
