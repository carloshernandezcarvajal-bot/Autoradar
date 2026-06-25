import math
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.listing import Listing
from app.models.vehicle import Vehicle
from app.schemas.schemas import SearchParams, ListingWithScore
from app.services.opportunity_score import calculate_score, calculate_market_stats

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=dict)
async def search_vehicles(params: SearchParams, db: AsyncSession = Depends(get_db)):
    conditions = [Listing.is_active == True]

    if params.q:
        like = f"%{params.q}%"
        conditions.append(
            Vehicle.brand.ilike(like)
            | Vehicle.model.ilike(like)
            | Vehicle.version.ilike(like)
        )
    if params.brand:
        conditions.append(Vehicle.brand == params.brand)
    if params.model:
        conditions.append(Vehicle.model == params.model)
    if params.year_min:
        conditions.append(Vehicle.year >= params.year_min)
    if params.year_max:
        conditions.append(Vehicle.year <= params.year_max)
    if params.price_min:
        conditions.append(Listing.current_price >= params.price_min)
    if params.price_max:
        conditions.append(Listing.current_price <= params.price_max)

    need_join = any([
        params.q, params.brand, params.model,
        params.year_min, params.year_max
    ])

    if need_join:
        base = select(Listing).join(Vehicle, Listing.vehicle_id == Vehicle.id)
        count_q = select(func.count()).select_from(Listing).join(Vehicle, Listing.vehicle_id == Vehicle.id).where(*conditions)
        query = base.where(*conditions).options(selectinload(Listing.vehicle))
    else:
        base = select(Listing)
        count_q = select(func.count()).select_from(Listing).where(*conditions)
        query = base.where(*conditions).options(selectinload(Listing.vehicle))

    total = (await db.execute(count_q)).scalar() or 0

    query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    result = await db.execute(query)
    listings = result.scalars().all()

    stats = {"avg": 0, "median": 0, "p25": 0, "p75": 0, "count": 0}
    if listings:
        brand = params.brand or listings[0].vehicle.brand
        model = params.model or listings[0].vehicle.model
        similar = (
            select(Listing)
            .join(Vehicle, Listing.vehicle_id == Vehicle.id)
            .where(Listing.is_active == True, Vehicle.brand == brand, Vehicle.model == model)
        )
        similar_result = await db.execute(similar)
        similar_listings = similar_result.scalars().all()
        if similar_listings:
            stats = await calculate_market_stats(similar_listings)

    items = []
    for listing in listings:
        days_published = 0
        if listing.date_found:
            if listing.date_found.tzinfo is None:
                now = datetime.now()
            else:
                now = datetime.now(timezone.utc)
            days_published = (now - listing.date_found).days
        mileage = listing.vehicle.mileage if listing.vehicle else None
        year = listing.vehicle.year if listing.vehicle else 0
        score = calculate_score(
            price=listing.current_price,
            market_avg=stats["avg"],
            mileage=mileage,
            year=year,
            days_published=days_published,
        )
        items.append(
            ListingWithScore(
                id=listing.id,
                vehicle_id=listing.vehicle_id,
                source=listing.source,
                url=listing.url,
                current_price=listing.current_price,
                currency=listing.currency,
                date_found=listing.date_found,
                date_updated=listing.date_updated,
                is_active=listing.is_active,
                vehicle=listing.vehicle,
                opportunity_score=score["score"],
                score_label=score["label"],
            )
        )

    if params.sort_by == "price":
        items.sort(key=lambda x: x.current_price, reverse=params.sort_order == "desc")
    elif params.sort_by == "year":
        items.sort(key=lambda x: x.vehicle.year if x.vehicle else 0, reverse=params.sort_order == "desc")
    elif params.sort_by == "mileage":
        items.sort(key=lambda x: x.vehicle.mileage if x.vehicle else 0, reverse=params.sort_order == "desc")
    else:
        items.sort(key=lambda x: x.opportunity_score or 0, reverse=params.sort_order == "desc")

    return {
        "items": items,
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": math.ceil(total / params.page_size) if total > 0 else 0,
        "market_stats": stats,
    }
