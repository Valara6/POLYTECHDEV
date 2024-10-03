from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from auth import bp as auth_bp, init_login_manager
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_login import login_required, current_user
from datetime import datetime
from auth import checkRole

# Импорт моделей
from db.models import db, Role, User, Lot, Auction

# Инициализация Flask-приложения
app = Flask(__name__)

# Подключение конфигурации
app.config.from_pyfile('configure.py')

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

init_login_manager(app)

app.register_blueprint(auth_bp)

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_item', methods=['GET', 'POST'])
@login_required
@checkRole('add_item')
def add_item():
    if request.method=="POST":
        user_id=current_user.id
        item_name=request.form.get('lot_name')
        item_description=request.form.get('description')
        item_price=request.form.get('price')
        try:
            new_item= Lot(
            lot_name=item_name,
            description=item_description,
            price=item_price,
            user_id=user_id)
            
            db.session.add(new_item)
            db.session.commit()
            flash('Вы успешно добавили предмет', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении предмета: {str(e)}', 'danger')
    return render_template('add_item.html')

@app.route('/create_auction', methods=['GET', 'POST'])
@login_required
@checkRole('create_auction')
def create_auction():
    if request.method=="POST":
        auction_name=request.form.get('auction_name')
        auction_description=request.form.get('auction_description')
        auction_place=request.form.get('auction_place')
        auction_date=request.form.get('auction_date')
        auction_time=request.form.get('auction_time') 

        try:
            # Преобразуем строку в объект datetime.date
            auction_date_obj = datetime.strptime(auction_date, '%Y-%m-%d').date()
            
            # Преобразуем строку в объект datetime.time
            auction_time_obj = datetime.strptime(auction_time, '%H:%M').time()

            new_auction= Auction(
            auction_name=auction_name,
            description=auction_description,
            place=auction_place,
            auction_date=auction_date_obj,
            auction_time = auction_time_obj)
            
            db.session.add(new_auction)
            db.session.commit()
            flash('Вы успешно добавили Аукцион', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении аукциона: {str(e)}', 'danger')
    return render_template('create_auction.html')

if __name__ == '__main__':
   app.run(host='0.0.0.0')
