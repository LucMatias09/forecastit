from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app import db
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso negado. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/employees')
@login_required
@admin_required
def list_employees():
    employees = User.query.all()
    return render_template('admin/employees.html', employees=employees)

@admin.route('/admin/pending-approvals')
@login_required
@admin_required
def pending_approvals():
    pending_users = User.query.filter_by(pending_approval=True).all()
    return render_template('admin/pending_approvals.html', pending_users=pending_users)

@admin.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if not user.pending_approval:
            return jsonify({'success': False, 'message': 'Este usuário não está pendente de aprovação.'})
        
        user.is_approved = True
        user.pending_approval = False
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin.route('/admin/reject/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if not user.pending_approval:
            return jsonify({'success': False, 'message': 'Este usuário não está pendente de aprovação.'})
        
        user.is_approved = False
        user.pending_approval = False
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin.route('/admin/employees', methods=['POST'])
@login_required
@admin_required
def create_employee():
    try:
        data = request.form
        
        # Verificar se o email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email já cadastrado'})
        
        new_employee = User(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            department=data['department'],
            role=data['role'],
            vacation_days=int(data['vacation_days']),
            is_approved=True,  # Funcionários criados pelo admin já são aprovados
            pending_approval=False
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin.route('/admin/employees/<int:employee_id>', methods=['GET'])
@login_required
@admin_required
def get_employee(employee_id):
    employee = User.query.get_or_404(employee_id)
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'email': employee.email,
        'department': employee.department,
        'role': employee.role,
        'vacation_days': employee.vacation_days
    })

@admin.route('/admin/employees/<int:employee_id>', methods=['PUT'])
@login_required
@admin_required
def update_employee(employee_id):
    try:
        employee = User.query.get_or_404(employee_id)
        data = request.form
        
        # Verificar se o novo email já existe para outro usuário
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != employee_id:
            return jsonify({'success': False, 'message': 'Email já cadastrado'})
        
        employee.name = data['name']
        employee.email = data['email']
        if data.get('password'):  # Atualiza a senha apenas se fornecida
            employee.password = generate_password_hash(data['password'])
        employee.department = data['department']
        employee.role = data['role']
        employee.vacation_days = int(data['vacation_days'])
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin.route('/admin/employees/<int:employee_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_employee(employee_id):
    try:
        employee = User.query.get_or_404(employee_id)
        
        # Impedir a exclusão do próprio usuário admin
        if employee.id == current_user.id:
            return jsonify({'success': False, 'message': 'Você não pode excluir sua própria conta'})
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
