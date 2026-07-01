from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.price_history import PriceHistory
from app.services.scraper import VendeTuNaveScraper, CarroYaScraper
from app.services.normalization import normalize_brand, normalize_model


async def _find_vehicle(db: AsyncSession, brand: str, model: str, year: int) -> Vehicle | None:
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.brand == brand,
            Vehicle.model == model,
            Vehicle.year == year,
        )
    )
    return result.scalar_one_or_none()


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

    vehicle = await _find_vehicle(db, brand, model, year)
    if not vehicle:
        vehicle = Vehicle(
            brand=brand,
            model=model,
            year=year,
            mileage=data.get("mileage"),
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
    results = {"vendetunave": 0, "carroya": 0, "errors": [], "total": 0}

    if sources is None:
        sources = ["vendetunave", "carroya"]

    scrape_tasks = []

    if "vendetunave" in sources:
        vendetunave = VendeTuNaveScraper()
        scrape_tasks.append(("vendetunave", vendetunave.scrape(max_pages=20)))

    if "carroya" in sources:
        carroya = CarroYaScraper()
        scrape_tasks.append(("carroya", carroya.scrape(max_pages=70)))

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
