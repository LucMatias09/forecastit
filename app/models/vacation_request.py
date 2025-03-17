from datetime import datetime
from app import db

class VacationRequest(db.Model):
    __tablename__ = 'vacation_request'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    justification = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    response_date = db.Column(db.DateTime)
    response_justification = db.Column(db.Text)
    
    # Relacionamento com User (usando lazy='joined' e join_depth=1 para evitar duplicação)
    requester = db.relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='vacation_requests',
        lazy='joined',
        join_depth=1
    )
    
    def __repr__(self):
        return f'<VacationRequest {self.id} - {self.requester.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.requester.name,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'days_requested': self.days_requested,
            'request_date': self.request_date.strftime('%Y-%m-%d %H:%M'),
            'response_date': self.response_date.strftime('%Y-%m-%d %H:%M') if self.response_date else None,
            'justification': self.justification,
            'response_justification': self.response_justification
        }
