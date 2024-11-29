import os

ADMIN_ROLE_ID=1
SELLER_ROLE_ID=3

# Абсолютный путь к директории с базой данных

basedir = os.path.abspath(os.path.dirname(__file__))

# Конфигурация базы данных с указанием пути к файлу в папке db
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db', 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Установка секретного ключа для сессий
SECRET_KEY='b3baa1cb519a5651c472d1afa1b3f4e04f1adf6909dae88a4cd39adc0ddd9732'#nosec
