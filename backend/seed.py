import asyncio
import random
import bcrypt
from datetime import datetime, timezone, timedelta

from app.database import engine, Base, async_session
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.price_history import PriceHistory
from app.models.user import User

SAMPLE_DATA = [
    {"brand": "Mazda", "model": "CX-5", "version": "Grand Touring", "year": 2021, "mileage": 35000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 115000000},
    {"brand": "Mazda", "model": "CX-5", "version": "Grand Touring", "year": 2022, "mileage": 18000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Medellín", "price": 125000000},
    {"brand": "Mazda", "model": "CX-5", "version": "Touring", "year": 2020, "mileage": 45000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Cali", "price": 98000000},
    {"brand": "Mazda", "model": "CX-5", "version": "Sport", "year": 2019, "mileage": 60000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 85000000},
    {"brand": "Mazda", "model": "CX-30", "version": "Signature", "year": 2023, "mileage": 12000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Medellín", "price": 110000000},
    {"brand": "Chevrolet", "model": "Tracker", "version": "Premier", "year": 2023, "mileage": 10000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 92000000},
    {"brand": "Chevrolet", "model": "Tracker", "version": "LTZ", "year": 2022, "mileage": 25000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Barranquilla", "price": 78000000},
    {"brand": "Chevrolet", "model": "Tracker", "version": "LT", "year": 2021, "mileage": 40000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Cali", "price": 65000000},
    {"brand": "Chevrolet", "model": "Onix", "version": "LTZ", "year": 2023, "mileage": 15000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Bogotá", "price": 58000000},
    {"brand": "Chevrolet", "model": "Onix", "version": "LT", "year": 2022, "mileage": 30000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Medellín", "price": 52000000},
    {"brand": "Renault", "model": "Stepway", "version": "Zen", "year": 2023, "mileage": 8000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Bogotá", "price": 55000000},
    {"brand": "Renault", "model": "Stepway", "version": "Intense", "year": 2022, "mileage": 20000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Cali", "price": 48000000},
    {"brand": "Renault", "model": "Duster", "version": "Intense", "year": 2023, "mileage": 12000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Medellín", "price": 82000000},
    {"brand": "Toyota", "model": "Corolla", "version": "HEV", "year": 2023, "mileage": 5000, "fuel_type": "Híbrido", "transmission": "Automática", "city": "Bogotá", "price": 115000000},
    {"brand": "Toyota", "model": "Corolla", "version": "XEI", "year": 2022, "mileage": 22000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 88000000},
    {"brand": "Toyota", "model": "Hilux", "version": "4x4 Diesel", "year": 2021, "mileage": 50000, "fuel_type": "Diesel", "transmission": "Manual", "city": "Medellín", "price": 145000000},
    {"brand": "Nissan", "model": "Versa", "version": "Sense", "year": 2023, "mileage": 7000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Cali", "price": 58000000},
    {"brand": "Nissan", "model": "Versa", "version": "Advance", "year": 2022, "mileage": 18000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 65000000},
    {"brand": "Hyundai", "model": "Tucson", "version": "N Line", "year": 2023, "mileage": 8000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Medellín", "price": 110000000},
    {"brand": "Hyundai", "model": "Accent", "version": "Vision", "year": 2022, "mileage": 25000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Barranquilla", "price": 49000000},
    {"brand": "Kia", "model": "Sportage", "version": "EX", "year": 2023, "mileage": 10000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 105000000},
    {"brand": "Kia", "model": "Rio", "version": "EX", "year": 2022, "mileage": 20000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Cali", "price": 52000000},
    {"brand": "Volkswagen", "model": "T-Cross", "version": "Comfortline", "year": 2023, "mileage": 9000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 95000000},
    {"brand": "Volkswagen", "model": "T-Cross", "version": "Trendline", "year": 2022, "mileage": 28000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Medellín", "price": 78000000},
    {"brand": "Suzuki", "model": "Vitara", "version": "GLX", "year": 2023, "mileage": 11000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 88000000},
    {"brand": "Suzuki", "model": "Swift", "version": "GL", "year": 2022, "mileage": 15000, "fuel_type": "Gasolina", "transmission": "Manual", "city": "Cali", "price": 55000000},
    {"brand": "Ford", "model": "Ranger", "version": "Wildtrak", "year": 2022, "mileage": 35000, "fuel_type": "Diesel", "transmission": "Automática", "city": "Medellín", "price": 140000000},
    {"brand": "BMW", "model": "Serie 1", "version": "118i", "year": 2021, "mileage": 30000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 110000000},
    {"brand": "Mercedes-Benz", "model": "GLA 200", "version": "AMG Line", "year": 2022, "mileage": 15000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 165000000},
    {"brand": "Mazda", "model": "CX-5", "version": "Signature", "year": 2023, "mileage": 5000, "fuel_type": "Gasolina", "transmission": "Automática", "city": "Bogotá", "price": 140000000},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        demo = User(
            email="demo@autoradar.co",
            password_hash=bcrypt.hashpw("demo123".encode(), bcrypt.gensalt()).decode()
        )
        session.add(demo)

        for item in SAMPLE_DATA:
            vehicle = Vehicle(
                brand=item["brand"],
                model=item["model"],
                version=item["version"],
                year=item["year"],
                mileage=item["mileage"],
                fuel_type=item["fuel_type"],
                transmission=item["transmission"],
                city=item["city"],
            )
            session.add(vehicle)
            await session.flush()

            source = random.choice(["tucarro", "carroya"])
            days_ago = random.randint(1, 30)
            listing = Listing(
                vehicle_id=vehicle.id,
                source=source,
                url=f"https://{'tucarro' if source == 'tucarro' else 'carroya'}.com.co/vehiculo-{vehicle.id}",
                current_price=item["price"],
                currency="COP",
                date_found=datetime.now(timezone.utc) - timedelta(days=days_ago),
                date_updated=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 3)),
                is_active=True,
            )
            session.add(listing)
            await session.flush()

            for d in range(days_ago, 0, -5):
                ph = PriceHistory(
                    listing_id=listing.id,
                    price=item["price"] * (1 + random.uniform(-0.05, 0.05)),
                    date=datetime.now(timezone.utc) - timedelta(days=d),
                )
                session.add(ph)

        await session.commit()
        print(f"Seed completo: {len(SAMPLE_DATA)} vehiculos insertados")
        print("Usuario demo: demo@autoradar.co / demo123")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
