"""Test the API directly using FastAPI TestClient."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
from app.database import engine, Base, async_session
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.price_history import PriceHistory
from app.models.user import User
import bcrypt
import json
from datetime import datetime, timezone, timedelta
import random

from httpx import AsyncClient, ASGITransport


async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        exists = await session.execute(__import__("sqlalchemy").select(User).where(User.email == "demo@autoradar.co"))
        if not exists.scalar_one_or_none():
            user = User(email="demo@autoradar.co", password_hash=bcrypt.hashpw(b"demo123", bcrypt.gensalt()).decode())
            session.add(user)

        count = await session.execute(__import__("sqlalchemy").select(__import__("sqlalchemy").func.count()).select_from(Vehicle))
        if count.scalar() == 0:
            brands_models = [
                ("Mazda", "CX-5", "Grand Touring", 2021, 35000, "Bogota", 115000000),
                ("Mazda", "CX-5", "Touring", 2020, 45000, "Cali", 98000000),
                ("Mazda", "CX-5", "Sport", 2019, 60000, "Bogota", 85000000),
                ("Mazda", "CX-30", "Signature", 2023, 12000, "Medellin", 110000000),
                ("Chevrolet", "Tracker", "Premier", 2023, 10000, "Bogota", 92000000),
                ("Chevrolet", "Tracker", "LTZ", 2022, 25000, "Barranquilla", 78000000),
                ("Chevrolet", "Onix", "LTZ", 2023, 15000, "Bogota", 58000000),
                ("Renault", "Stepway", "Zen", 2023, 8000, "Bogota", 55000000),
                ("Renault", "Duster", "Intense", 2023, 12000, "Medellin", 82000000),
                ("Toyota", "Corolla", "HEV", 2023, 5000, "Bogota", 115000000),
                ("Toyota", "Corolla", "XEI", 2022, 22000, "Bogota", 88000000),
                ("Nissan", "Versa", "Sense", 2023, 7000, "Cali", 58000000),
                ("Hyundai", "Tucson", "N Line", 2023, 8000, "Medellin", 110000000),
                ("Kia", "Sportage", "EX", 2023, 10000, "Bogota", 105000000),
                ("Volkswagen", "T-Cross", "Comfortline", 2023, 9000, "Bogota", 95000000),
            ]
            for b, m, v, y, mi, c, p in brands_models:
                veh = Vehicle(brand=b, model=m, version=v, year=y, mileage=mi, city=c)
                session.add(veh)
                await session.flush()
                src = random.choice(["tucarro", "carroya"])
                days = random.randint(1, 20)
                listing = Listing(
                    vehicle_id=veh.id, source=src,
                    url=f"https://{src}.com/vehiculo-{veh.id}",
                    current_price=p, currency="COP",
                    date_found=datetime.now(timezone.utc) - timedelta(days=days),
                    is_active=True,
                )
                session.add(listing)
            await session.commit()
    print("DB setup OK")


async def run_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health
        r = await client.get("/api/health")
        print(f"Health: {r.json()}")

        # Brands
        r = await client.get("/api/vehicles/brands/list")
        print(f"Brands: {r.json()}")

        # Search
        r = await client.post("/api/search", json={"brand": "Mazda", "page": 1, "page_size": 5})
        data = r.json()
        print(f"\nSearch Mazda: {data['total']} results (HTTP {r.status_code})")
        if r.status_code == 200:
            for item in data["items"][:3]:
                v = item["vehicle"]
                print(f"  {v['brand']} {v['model']} {v['year']} - ${item['current_price']:,.0f} - Score: {item['opportunity_score']} ({item['score_label']})")

        # Search all
        r = await client.post("/api/search", json={"page": 1, "page_size": 5})
        data = r.json()
        print(f"\nAll: {data['total']} total (HTTP {r.status_code})")

        # Login
        r = await client.post("/api/auth/login", json={"email": "demo@autoradar.co", "password": "demo123"})
        if r.status_code == 200:
            token = r.json()["access_token"]
            print(f"\nLogin OK - token: {token[:20]}...")

            # Add favorite
            headers = {"Authorization": f"Bearer {token}"}
            r2 = await client.post("/api/favorites", json={"listing_id": 1}, headers=headers)
            print(f"Favorite: {r2.status_code} - {r2.json()}")
        else:
            print(f"\nLogin failed: {r.status_code} - {r.text}")

    await engine.dispose()
    print("\n=== All tests done ===")


if __name__ == "__main__":
    asyncio.run(setup_db())
    asyncio.run(run_tests())
