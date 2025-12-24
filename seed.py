from backend.app import create_app, db
from backend.models import User
from werkzeug.security import generate_password_hash

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created.")

        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            user = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(user)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db()
