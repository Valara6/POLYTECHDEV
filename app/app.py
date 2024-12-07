from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from auth import bp as auth_bp, init_login_manager
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_login import login_required, current_user
from datetime import datetime
from auth import checkRole
from flask_migrate import Migrate

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
    auctions = db.session.execute(db.select(Auction)).scalars()
    return render_template('index.html', auctions=auctions)


@app.route('/add_item/<int:auction_id>', methods=['GET', 'POST'])
@login_required
@checkRole('add_item')
def add_item(auction_id):
    if request.method == "POST":
        user_id = current_user.id
        item_name = request.form.get('lot_name')
        item_description = request.form.get('description')
        item_price = request.form.get('price')
        
        try:
            new_item = Lot(
                lot_name=item_name,
                description=item_description,
                price=item_price,
                user_id=user_id,
                auction_id=auction_id  # Связываем предмет с аукционом
            )
            
            db.session.add(new_item)
            db.session.commit()
            flash('Вы успешно добавили предмет на аукцион', 'success')
            return redirect(url_for('view_auction', auction_id=auction_id))
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

@app.route('/auction/<int:auction_id>', methods=['GET'])
def view_auction(auction_id):
    auction = db.session.query(Auction).filter_by(id=auction_id).first()
    items = db.session.query(Lot).filter_by(auction_id=auction_id).all()  # Получаем все предметы на аукционе
    return render_template('view_auction.html', auction=auction, items=items)


@app.route('/delete_auction/<int:auction_id>', methods=['POST'])
def delete_auction(auction_id):
    auction = db.session.get(Auction, auction_id)
    if auction:
        db.session.delete(auction)
        db.session.commit()
        flash("Аукцион удалён.", "success")
    else:
        flash("Аукцион не найден.", "error")
    return redirect(url_for('index'))  # Замените 'index' на имя вашего маршрута

