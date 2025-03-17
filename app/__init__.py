from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuração
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "app.db"))}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Registro dos blueprints
    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.vacation import vacation
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(vacation)
    
    # Configuração do login manager
    from app.models.user import User
    from app.models.vacation_request import VacationRequest
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    @app.context_processor
    def utility_processor():
        def get_pending_count():
            if not current_user.is_authenticated:
                return 0
                
            if current_user.role == 'admin':
                return VacationRequest.query.filter_by(status='pending').count()
            else:
                return VacationRequest.query.filter_by(
                    user_id=current_user.id,
                    status='pending'
                ).count()
                
        return dict(pending_count=get_pending_count())
        
    return app
