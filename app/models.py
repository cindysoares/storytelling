from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class CurrentStatus(Base):
    __tablename__ = "current_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
