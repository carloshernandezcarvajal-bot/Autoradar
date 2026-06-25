import statistics
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.models.vehicle import Vehicle
from app.models.price_history import PriceHistory


async def calculate_market_stats(listings: list[Listing]) -> dict:
    prices = [l.current_price for l in listings if l.current_price > 0]
    if not prices:
        return {"avg": 0, "median": 0, "p25": 0, "p75": 0, "count": 0}
    prices.sort()
    return {
        "avg": statistics.mean(prices),
        "median": statistics.median(prices),
        "p25": prices[len(prices) // 4] if len(prices) >= 4 else prices[0],
        "p75": prices[(3 * len(prices)) // 4] if len(prices) >= 4 else prices[-1],
        "count": len(prices),
    }


def calculate_score(
    price: float,
    market_avg: float,
    mileage: int | None,
    year: int,
    days_published: int,
) -> dict:
    if market_avg <= 0 or price <= 0:
        return {"score": 50.0, "label": "Precio normal"}

    price_ratio = price / market_avg
    price_score = max(0, min(100, (1 - price_ratio) * 100 + 50))

    current_year = datetime.now(timezone.utc).year
    age = current_year - year
    age_score = max(0, min(100, (1 - age / 30) * 100))

    if mileage is not None and mileage > 0:
        expected_mileage = age * 20000
        mileage_ratio = mileage / expected_mileage if expected_mileage > 0 else 1
        mileage_score = max(0, min(100, (1 - mileage_ratio) * 100 + 50))
    else:
        mileage_score = 50

    time_score = max(0, min(100, (1 - days_published / 90) * 100))

    score = (
        price_score * 0.50
        + mileage_score * 0.20
        + age_score * 0.15
        + time_score * 0.15
    )

    score = max(0, min(100, score))

    if score >= 80:
        label = "Excelente oportunidad"
    elif score >= 60:
        label = "Buena oportunidad"
    elif score >= 40:
        label = "Precio normal"
    else:
        label = "Sobrevalorado"

    return {"score": round(score, 1), "label": label}


async def score_listing(
    listing: Listing, db: AsyncSession
) -> dict:
    vehicle = listing.vehicle

    similar = await db.execute(
        select(Listing)
        .join(Listing.vehicle)
        .where(Vehicle.brand == vehicle.brand)
        .where(Vehicle.model == vehicle.model)
        .where(Vehicle.year == vehicle.year)
        .where(Listing.is_active == True)
    )
    similar_listings = similar.scalars().all()
    stats = await calculate_market_stats(similar_listings)

    days_published = 0
    if listing.date_found:
        if listing.date_found.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(timezone.utc)
        days_published = (now - listing.date_found).days

    return calculate_score(
        price=listing.current_price,
        market_avg=stats["avg"],
        mileage=vehicle.mileage,
        year=vehicle.year,
        days_published=days_published,
    )

