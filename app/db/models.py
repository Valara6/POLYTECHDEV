from datetime import date, time, datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, MetaData, Boolean, Date, Time, TIMESTAMP
from werkzeug.security import generate_password_hash, check_password_hash
from configure import ADMIN_ROLE_ID, SELLER_ROLE_ID
from check_rights import CheckRights

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)

    # Установка значения по умолчанию
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True)  # Теперь nullable


    role = relationship("Role")

    def is_admin(self):
        return ADMIN_ROLE_ID == self.role_id
    
    def is_seller(self):
        return SELLER_ROLE_ID == self.role_id
    
    def can(self, action, record=None):
        check_rights = CheckRights(record)
        method = getattr(check_rights, action, None)
        if method:
            return method()
        return False

    def get_id(self) -> str:
        return str(self.id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Lot(Base):
    __tablename__ = 'lots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    auction_id: Mapped[int] = mapped_column(ForeignKey('auctions.id', ondelete="CASCADE"), nullable=True)

    user = relationship("User")
    auction = relationship("Auction", back_populates="lots")


    
class Auction(Base):
    __tablename__ = 'auctions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auction_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    place: Mapped[str] = mapped_column(String(255), nullable=False)
    auction_date: Mapped[date] = mapped_column(Date, nullable=False)
    auction_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Связь с Lot
    lots: Mapped[list['Lot']] = relationship(
        "Lot", back_populates="auction", cascade="all, delete-orphan"
    )


     






