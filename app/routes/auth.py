from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from functools import wraps

auth = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso negado. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_approved and user.role != 'admin':
                flash('Seu cadastro ainda não foi aprovado.', 'warning')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            return redirect(url_for('main.dashboard'))
            
        flash('Email ou senha incorretos.', 'error')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    departments = ['TI', 'RH', 'Financeiro', 'Marketing', 'Comercial', 'Operações']
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        
        if not all([name, email, password, department]):
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('auth/register.html', departments=departments)
            
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('auth/register.html', departments=departments)
            
        user = User(
            name=name,
            email=email,
            department=department,
            role='user',
            is_approved=False
        )
        user.set_password(password)
        
        # Primeiro usuário é admin
        if User.query.count() == 0:
            user.role = 'admin'
            user.is_approved = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Aguarde a aprovação do administrador.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', departments=departments)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.filter(User.id != current_user.id).all()
    departments = ['TI', 'RH', 'Financeiro', 'Marketing', 'Comercial', 'Operações']
    return render_template('auth/users.html', users=users, departments=departments)

@auth.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    if user_id == current_user.id:
        flash('Você não pode editar seu próprio usuário.', 'error')
        return redirect(url_for('auth.list_users'))
        
    user = User.query.get_or_404(user_id)
    departments = ['TI', 'RH', 'Financeiro', 'Marketing', 'Comercial', 'Operações']
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        role = request.form.get('role')
        vacation_days = request.form.get('vacation_days', type=int)
        new_password = request.form.get('password')
        
        if not all([name, email, department, role]):
            flash('Nome, email, departamento e função são obrigatórios.', 'error')
            return render_template('auth/edit_user.html', user=user, departments=departments)
            
        existing_user = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_user:
            flash('Este email já está cadastrado para outro usuário.', 'error')
            return render_template('auth/edit_user.html', user=user, departments=departments)
            
        user.name = name
        user.email = email
        user.department = department
        user.role = role
        if vacation_days is not None:
            user.vacation_days = vacation_days
        if new_password:
            user.set_password(new_password)
            
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('auth.list_users'))
    
    return render_template('auth/edit_user.html', user=user, departments=departments)

@auth.route('/users/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    if user_id == current_user.id:
        flash('Você não pode aprovar seu próprio usuário.', 'error')
        return redirect(url_for('auth.list_users'))
        
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    flash(f'Usuário {user.name} aprovado com sucesso!', 'success')
    return redirect(url_for('auth.list_users'))

@auth.route('/users/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    if user_id == current_user.id:
        flash('Você não pode rejeitar seu próprio usuário.', 'error')
        return redirect(url_for('auth.list_users'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Usuário {user.name} rejeitado com sucesso!', 'success')
    return redirect(url_for('auth.list_users'))
