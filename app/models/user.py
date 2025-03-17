from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='employee')
    vacation_days = db.Column(db.Integer, default=30)  # Padrão no Brasil
    department = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    pending_approval = db.Column(db.Boolean, default=True)
    
    # Relacionamento com VacationRequest (usando lazy='select' para evitar duplicação)
    vacation_requests = db.relationship(
        'VacationRequest',
        back_populates='requester',
        lazy='select',
        cascade='all, delete-orphan'
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_active(self):
        return self.is_approved
        
    def __repr__(self):
        return f'<User {self.email}>'
