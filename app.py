from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from backend.config import Config
from backend.models import db, User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'admin.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from backend.routes.api_public import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from backend.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create DB tables (simplest migration strategy for now)
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
