from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(80), index=True)
    model: Mapped[str] = mapped_column(String(120), index=True)
    version: Mapped[str | None] = mapped_column(String(200))
    year: Mapped[int] = mapped_column(Integer, index=True)
    mileage: Mapped[int | None] = mapped_column(Integer)
    fuel_type: Mapped[str | None] = mapped_column(String(40))
    transmission: Mapped[str | None] = mapped_column(String(40))
    color: Mapped[str | None] = mapped_column(String(40))
    city: Mapped[str | None] = mapped_column(String(100))
    image_url: Mapped[str | None] = mapped_column(String(500))
    license_plate_encrypted: Mapped[str | None] = mapped_column(String(500))

    listings: Mapped[list["Listing"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")
