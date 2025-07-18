from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
import datetime
from sqlalchemy import BigInteger, Integer, String, DateTime, func, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    selected_model: Mapped[str] = mapped_column(String(100), default="deepseek/deepseek-chat")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ref_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    registered_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    description: Mapped[str] = mapped_column(Text)              # Текст задания
    file_id: Mapped[str | None] = mapped_column(String(255))    # Telegram file_id документа (если есть)

    status: Mapped[str] = mapped_column(String(50), default="new")  # new / in_progress / complete / canceled
    stars_given: Mapped[bool] = mapped_column(Boolean, default=False)  # Флаг: выданы ли звезды за сделку

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

