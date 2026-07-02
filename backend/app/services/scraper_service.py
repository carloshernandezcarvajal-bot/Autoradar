from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.price_history import PriceHistory
from app.services.scraper import VendeTuNaveScraper, CarroYaScraper, SegundazoScraper, ListoYaAutosScraper, CarMaxScraper
from app.services.normalization import normalize_brand, normalize_model


async def _find_vehicle(db: AsyncSession, brand: str, model: str, year: int, mileage: int | None, color: str | None, city: str | None, plate: str | None) -> Vehicle | None:
    if plate:
        result_plate = await db.execute(
            select(Vehicle).where(Vehicle.license_plate_encrypted == plate)
        )
        vehicle_plate = result_plate.scalar_one_or_none()
        if vehicle_plate:
            return vehicle_plate

    query = select(Vehicle).where(
        Vehicle.brand == brand,
        Vehicle.model == model,
        Vehicle.year == year
    )
    
    if mileage is not None:
        query = query.where(Vehicle.mileage == mileage)
    else:
        query = query.where(Vehicle.mileage.is_(None))
        
    if color:
        query = query.where(Vehicle.color == color)
    else:
        query = query.where(Vehicle.color.is_(None))
        
    if city:
        query = query.where(Vehicle.city == city)
    else:
        query = query.where(Vehicle.city.is_(None))

    result = await db.execute(query)
    return result.scalars().first()


async def _save_listing(db: AsyncSession, vehicle_id: int, data: dict) -> Listing:
    source_id = data.get("source_id") or data.get("source_url", "")

    existing = await db.execute(
        select(Listing).where(
            Listing.source == data["source"],
            Listing.source_id == source_id,
        )
    )
    listing = existing.scalar_one_or_none()

    if listing:
        old_price = listing.current_price
        listing.current_price = data["price"]
        listing.date_updated = datetime.now(timezone.utc)
        listing.is_active = True
        listing.is_active = True

        if old_price != data["price"]:
            ph = PriceHistory(listing_id=listing.id, price=data["price"], date=datetime.now(timezone.utc))
            db.add(ph)
    else:
        listing = Listing(
            vehicle_id=vehicle_id,
            source=data["source"],
            source_id=source_id,
            url=data.get("source_url", ""),
            current_price=data["price"],
            currency=data.get("currency", "COP"),
            date_found=data.get("date_found", datetime.now(timezone.utc)),
            date_updated=datetime.now(timezone.utc),
            is_active=True,
        )
        db.add(listing)
        await db.flush()

        ph = PriceHistory(listing_id=listing.id, price=data["price"], date=datetime.now(timezone.utc))
        db.add(ph)

    return listing


async def _save_vehicle_data(db: AsyncSession, data: dict) -> dict:
    brand = normalize_brand(data.get("brand", ""))
    raw_model = data.get("model", "")
    model = normalize_model(brand, raw_model)
    year = data.get("year") or 0
    mileage = data.get("mileage")
    color = data.get("color")
    city = data.get("city")
    plate = data.get("license_plate_encrypted")

    vehicle = await _find_vehicle(db, brand, model, year, mileage, color, city, plate)
    if not vehicle:
        vehicle = Vehicle(
            brand=brand,
            model=model,
            version=data.get("version"),
            year=year,
            mileage=mileage,
            fuel_type=data.get("fuel_type"),
            transmission=data.get("transmission"),
            color=color,
            city=city,
            image_url=data.get("image_url"),
            license_plate_encrypted=plate,
        )
        db.add(vehicle)
        await db.flush()

    listing = await _save_listing(db, vehicle.id, data)
    await db.commit()

    return {
        "listing_id": listing.id,
        "vehicle_id": vehicle.id,
        "brand": brand,
        "model": model,
        "year": year,
        "price": listing.current_price,
        "source": data["source"],
    }


async def run_scrape(sources: list[str] | None = None) -> dict:
    results = {"vendetunave": 0, "carroya": 0, "segundazo": 0, "listoya": 0, "carmax": 0, "errors": [], "total": 0}

    if sources is None:
        sources = ["vendetunave", "carroya", "segundazo", "listoya", "carmax"]

    scrape_tasks = []

    if "vendetunave" in sources:
        vendetunave = VendeTuNaveScraper()
        scrape_tasks.append(("vendetunave", vendetunave.scrape(max_pages=20)))

    if "carroya" in sources:
        carroya = CarroYaScraper()
        scrape_tasks.append(("carroya", carroya.scrape(max_pages=70)))

    if "segundazo" in sources:
        segundazo = SegundazoScraper()
        scrape_tasks.append(("segundazo", segundazo.scrape(max_pages=1)))

    if "listoya" in sources:
        listoya = ListoYaAutosScraper()
        scrape_tasks.append(("listoya", listoya.scrape(max_pages=10)))

    if "carmax" in sources:
        carmax = CarMaxScraper()
        scrape_tasks.append(("carmax", carmax.scrape(max_pages=6)))

    async with async_session() as db:
        for source_name, scrape_task in scrape_tasks:
            try:
                vehicles_data = await scrape_task
            except Exception as e:
                results["errors"].append(f"{source_name}: {str(e)}")
                continue

            for vdata in vehicles_data:
                try:
                    await _save_vehicle_data(db, vdata)
                    results[source_name] += 1
                    results["total"] += 1
                except Exception as e:
                    await db.rollback()
                    results["errors"].append(f"{source_name} item: {str(e)}")

        await db.commit()

    return results
