from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.vacation_request import VacationRequest
from app.models.user import User
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Buscar todas as solicitações de férias (aprovadas e pendentes)
    if current_user.role == 'admin':
        vacation_requests = VacationRequest.query\
            .filter(or_(VacationRequest.status == 'approved',
                       VacationRequest.status == 'pending'))\
            .all()
    else:
        # Para usuários normais, mostrar apenas do seu departamento
        department_users = User.query.filter_by(department=current_user.department).all()
        department_user_ids = [user.id for user in department_users]
        vacation_requests = VacationRequest.query\
            .filter(VacationRequest.user_id.in_(department_user_ids))\
            .filter(or_(VacationRequest.status == 'approved',
                       VacationRequest.status == 'pending'))\
            .all()
    
    # Converter solicitações em eventos para o calendário
    vacation_events = []
    for request in vacation_requests:
        # Definir cores baseado no status
        if request.status == 'approved':
            bg_color = '#28a745'  # Verde para aprovadas
            text_color = '#ffffff'
        else:
            bg_color = '#ffc107'  # Amarelo para pendentes
            text_color = '#000000'
        
        event = {
            'title': f'{request.requester.name} - {request.status.capitalize()}',
            'start': request.start_date.strftime('%Y-%m-%d'),
            'end': request.end_date.strftime('%Y-%m-%d'),
            'backgroundColor': bg_color,
            'borderColor': bg_color,
            'textColor': text_color,
            'extendedProps': {
                'status': request.status,
                'department': request.requester.department
            }
        }
        vacation_events.append(event)
    
    return render_template('main/dashboard.html', 
                         approved_vacation_events=vacation_events,
                         current_department=current_user.department)

@main.route('/calendar')
@login_required
def calendar():
    return render_template('main/calendar.html')
