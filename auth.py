from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from db.models import db, User, Role
from sqlalchemy.exc import SQLAlchemyError
import hashlib
import regex as re

bp = Blueprint('auth', __name__, url_prefix='/auth')

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    print(f"Loading user: {user}")  # Для отладки
    return user

def checkRole(action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.can(action):
                return f(*args, **kwargs)
            flash("У вас нет доступа к этой странице", "danger")
            return redirect(url_for('index'))
        return wrapper
    return decorator


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')
        if username and password:
            user = db.session.query(User).filter_by(username=username).first()
            if user:
                if check_password_hash(user.password_hash, password):
                    login_user(user)
                    flash('Вы успешно аутентифицированы.', 'success')
                    next = request.args.get('next')
                    return redirect(url_for('index'))
                else:
                    flash('Неверный пароль.', 'danger')
            else:
                flash('Пользователь не найден.', 'danger')
        else:
            flash('Пожалуйста, введите логин и пароль.', 'danger')
    return render_template('auth/login.html')

@bp.route('/create_user', methods=['GET', 'POST'])
def create_user():
    errors = {}
    if request.method == "POST": 
        first_name = request.form.get('name')
        second_name = request.form.get('lastname')
        middle_name = request.form.get('middlename')
        login = request.form.get('login')
        password = request.form.get('password')
        role_id=request.form.get('role')
        print(role_id)
        
        ##validation##

        if login and not re.match(r'^[a-zA-Z0-9]{5,}$', login):
            errors['login'] = errors.get('login', '') + ' Логин должен состоять только из латинских букв и цифр и иметь длину не менее 5 символов.'
        
        if len(password) < 8 or len(password) > 128:
                errors['password'] = errors.get('password', '') + ' Пароль должен быть не менее 8 и не более 128 символов.'
        print(errors)


        if errors:
            return render_template('auth/create_user.html', errors=errors)
        try:
            # Хешируем пароль перед сохранением в базу данных
            password_hash = generate_password_hash(password)
            
            # Создаем нового пользователя
            new_user = User(
                username=login,
                password_hash=password_hash,
                first_name=first_name,
                last_name=second_name,
                middle_name=middle_name,
                role_id=role_id,
                is_active=1
            )
            
            # Добавляем пользователя в сессию
            db.session.add(new_user)
            db.session.commit()  # Сохраняем изменения
            
            flash('Вы успешно зарегистрировали пользователя', 'success')
            return redirect(url_for('auth.login'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')

    return render_template('auth/create_user.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))