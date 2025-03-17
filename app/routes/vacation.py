from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.vacation_request import VacationRequest
from app.models.user import User
from functools import wraps
from sqlalchemy import or_

vacation = Blueprint('vacation', __name__)

MAX_VACATION_DAYS = 24

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso negado. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@vacation.route('/vacation/request', methods=['GET', 'POST'])
@login_required
def request_vacation():
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            justification = request.form.get('justification', '')
            
            # Calcular dias úteis (simplificado - pode ser melhorado para considerar feriados)
            days_requested = (end_date - start_date).days + 1
            
            # Verificar se não excede o máximo de dias
            if days_requested > MAX_VACATION_DAYS:
                return jsonify({
                    'success': False,
                    'message': f'Você não pode solicitar mais que {MAX_VACATION_DAYS} dias de férias.'
                })
            
            # Verificar se tem dias suficientes
            if days_requested > current_user.vacation_days:
                return jsonify({
                    'success': False,
                    'message': f'Você só tem {current_user.vacation_days} dias de férias disponíveis.'
                })
            
            # Verificar se já existe solicitação pendente
            pending_request = VacationRequest.query.filter_by(
                user_id=current_user.id,
                status='pending'
            ).first()
            
            if pending_request:
                return jsonify({
                    'success': False,
                    'message': 'Você já tem uma solicitação de férias pendente.'
                })
            
            # Criar nova solicitação
            vacation_request = VacationRequest(
                user_id=current_user.id,
                start_date=start_date,
                end_date=end_date,
                days_requested=days_requested,
                justification=justification
            )
            
            db.session.add(vacation_request)
            db.session.commit()
            
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
            
    return render_template('vacation/request.html', max_vacation_days=MAX_VACATION_DAYS)

@vacation.route('/vacation/history')
@login_required
def vacation_history():
    # Query base para todas as solicitações
    base_query = VacationRequest.query
    
    # Filtrar por departamento se não for admin
    if current_user.role != 'admin':
        base_query = base_query.join(User).filter(User.department == current_user.department)
    
    # Executar a query ordenando por data
    requests = base_query.order_by(VacationRequest.request_date.desc()).all()
    
    return render_template('vacation/history.html', requests=requests)

@vacation.route('/vacation/pending')
@login_required
@admin_required
def pending_requests():
    # Query simples e direta para solicitações pendentes
    pending = VacationRequest.query\
        .filter_by(status='pending')\
        .order_by(VacationRequest.request_date.asc())\
        .all()
    
    return render_template('vacation/pending.html', pending_requests=pending)

@vacation.route('/vacation/approve/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def approve_request(request_id):
    try:
        vacation_request = VacationRequest.query.get_or_404(request_id)
        justification = request.form.get('justification', '')
        
        if vacation_request.status != 'pending':
            return jsonify({
                'success': False,
                'message': 'Esta solicitação não está mais pendente.'
            })
        
        # Verificar se ainda tem dias suficientes
        user = User.query.get(vacation_request.user_id)
        if vacation_request.days_requested > user.vacation_days:
            return jsonify({
                'success': False,
                'message': f'O funcionário só tem {user.vacation_days} dias de férias disponíveis.'
            })
        
        # Aprovar solicitação
        vacation_request.status = 'approved'
        vacation_request.response_date = datetime.utcnow()
        vacation_request.response_justification = justification
        
        # Deduzir dias de férias
        user.vacation_days -= vacation_request.days_requested
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vacation.route('/vacation/reject/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def reject_request(request_id):
    try:
        vacation_request = VacationRequest.query.get_or_404(request_id)
        justification = request.form.get('justification', '')
        
        if vacation_request.status != 'pending':
            return jsonify({
                'success': False,
                'message': 'Esta solicitação não está mais pendente.'
            })
        
        # Rejeitar solicitação
        vacation_request.status = 'rejected'
        vacation_request.response_date = datetime.utcnow()
        vacation_request.response_justification = justification
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
