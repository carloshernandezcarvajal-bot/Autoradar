from datetime import datetime, timezone

from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    source: Mapped[str] = mapped_column(String(40))
    source_id: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(1000))
    current_price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="COP")
    description: Mapped[str | None] = mapped_column(String(2000))
    date_found: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    date_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(default=True)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="listings")
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="listing", cascade="all, delete-orphan")
