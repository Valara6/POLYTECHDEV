import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db.models import db, Role, User, Lot, Auction
from app import app as main_app
from werkzeug.security import generate_password_hash
from configure import ADMIN_ROLE_ID, SELLER_ROLE_ID

@pytest.fixture
def app():
    """Создает экземпляр приложения для тестирования."""
    main_app.config['TESTING'] = True
    main_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    main_app.config['SECRET_KEY'] = 'test_secret_key'

    with main_app.app_context():
        db.create_all()  # Создание таблиц
        yield main_app  # Передача тестового приложения
        db.session.remove()  # Завершение сессии
        db.drop_all()  # Удаление таблиц


@pytest.fixture
def client(app):
    """Создает тестовый клиент."""
    return app.test_client()

@pytest.fixture
def session(app):
    """Создает сессию для взаимодействия с базой данных."""
    with app.app_context():
        yield db.session


@pytest.fixture
def init_roles(app):
    """Добавляет роли в тестовую базу данных."""
    with app.app_context():
        # Роль администратора
        admin_role = Role(id=ADMIN_ROLE_ID, name='Admin', description='Administrator')
        db.session.add(admin_role)
        # Роль продавца
        seller_role = Role(id=SELLER_ROLE_ID, name='Seller', description='Seller')
        db.session.add(seller_role)
        db.session.commit()

@pytest.fixture
def admin_user(app):
    """Создает тестового пользователя с ролью администратор."""
    with app.app_context():
        user = User(
            username='adminuser',
            password_hash=generate_password_hash('adminpassword'),
            first_name='Admin',
            last_name='User',
            middle_name='A.',
            role_id=ADMIN_ROLE_ID,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_user(app):
    """Создает тестового пользователя."""
    with app.app_context():
        user = User(
            username='testuser',
            password_hash=generate_password_hash('testpassword'),
            first_name='Test',
            last_name='User',
            middle_name='T.',
            role_id=1,
            is_active=True
        )
        with db.session.begin():  # Контекст для сессии
            db.session.add(user)

        # Используем сессию для запроса
        session = db.session
        return session.execute(db.select(User).filter_by(username='testuser')).scalar_one()

def test_index_page(client):
    """Проверка, что главная страница загружается."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Аукционы'.encode('utf-8') in response.data  # Проверяем наличие текста

def test_login_page(client):
    """Проверка отображения страницы логина."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert 'Логин'.encode('utf-8') in response.data

def test_create_user_page(client):
    """Проверка отображения страницы cоздания пользователя."""
    response = client.get('/auth/create_user')
    assert response.status_code == 200
    assert 'Создание пользователя'.encode('utf-8') in response.data

def test_successful_login(client, test_user):
    """Проверка успешного входа в систему."""
    response = client.post('/auth/login', data={
        'login': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно аутентифицированы.'.encode('utf-8') in response.data


def test_unsuccessful_login(client):
    """Проверка ошибки входа с неверным паролем."""
    response = client.post('/auth/login', data={
        'login': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Пользователь не найден.'.encode('utf-8') in response.data

def test_create_auction(client, test_user, session):
    """Тестирование создания аукциона."""
    with client.session_transaction() as flask_session:
        flask_session['_user_id'] = test_user.id  # Авторизуем пользователя

    response = client.post('/create_auction', data={
        'auction_name': 'Test Auction',
        'auction_description': 'This is a test auction.',
        'auction_place': 'Test Place',
        'auction_date': '2024-01-01',
        'auction_time': '12:00'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Вы успешно добавили Аукцион'.encode('utf-8') in response.data

    # Проверка в базе данных
    new_auction = session.execute(
        db.select(Auction).filter_by(auction_name='Test Auction')
    ).scalar_one()
    assert new_auction is not None

def test_create_user(client):
    """Тестирование регистрации пользователя."""
    response = client.post('/auth/create_user', data={
        'name': 'John',
        'lastname': 'Doe',
        'middlename': 'Middle',
        'login': 'newuser',
        'password': 'securepassword',
        'role': 1
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы успешно зарегистрировали пользователя'.encode('utf-8') in response.data

def test_unauthorized_access(client):
    """Проверка доступа без авторизации."""
    response = client.get('/create_auction', follow_redirects=True)
    assert response.status_code == 200
    assert 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'.encode('utf-8') in response.data
