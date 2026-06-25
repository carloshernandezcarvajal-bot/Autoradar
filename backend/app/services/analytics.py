from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.models.price_history import PriceHistory
from app.models.vehicle import Vehicle


async def get_price_history(
    listing_id: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.listing_id == listing_id)
        .order_by(PriceHistory.date)
    )
    return [
        {"date": ph.date.isoformat(), "price": ph.price}
        for ph in result.scalars().all()
    ]


async def get_market_summary(
    brand: str | None, model: str | None, year: int | None, db: AsyncSession
) -> dict:
    query = select(Listing).join(Vehicle).where(Listing.is_active == True)

    if brand:
        query = query.where(Vehicle.brand == brand)
    if model:
        query = query.where(Vehicle.model == model)
    if year:
        query = query.where(Vehicle.year == year)

    result = await db.execute(query)
    listings = result.scalars().all()

    if not listings:
        return {
            "count": 0,
            "avg_price": 0,
            "min_price": 0,
            "max_price": 0,
            "avg_mileage": 0,
            "total_listings": 0,
        }

    prices = [l.current_price for l in listings if l.current_price > 0]
    mileages = [
        l.vehicle.mileage for l in listings if l.vehicle and l.vehicle.mileage
    ]

    return {
        "count": len(listings),
        "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "avg_mileage": round(sum(mileages) / len(mileages)) if mileages else 0,
        "total_listings": len(listings),
    }
