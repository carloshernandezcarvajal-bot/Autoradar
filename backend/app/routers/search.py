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
        v_query = select(Vehicle.id).join(Listing, Listing.vehicle_id == Vehicle.id).where(*conditions).distinct()
    else:
        v_query = select(Listing.vehicle_id).where(*conditions).distinct()

    count_q = select(func.count()).select_from(v_query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    v_query = v_query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    v_result = await db.execute(v_query)
    vehicle_ids = [row[0] for row in v_result.all()]

    items = []
    stats = {"avg": 0, "median": 0, "p25": 0, "p75": 0, "count": 0}

    if vehicle_ids:
        # Cargar todos los listings activos de estos vehículos
        all_listings_q = (
            select(Listing)
            .where(Listing.vehicle_id.in_(vehicle_ids), Listing.is_active == True)
            .options(selectinload(Listing.vehicle))
        )
        all_listings_result = await db.execute(all_listings_q)
        all_listings = all_listings_result.scalars().all()

        # Agrupar en Python
        listings_by_vehicle = {}
        for l in all_listings:
            listings_by_vehicle.setdefault(l.vehicle_id, []).append(l)

        # Calcular stats de mercado si corresponde
        brand = params.brand or all_listings[0].vehicle.brand
        model = params.model or all_listings[0].vehicle.model
        similar = (
            select(Listing)
            .join(Vehicle, Listing.vehicle_id == Vehicle.id)
            .where(Listing.is_active == True, Vehicle.brand == brand, Vehicle.model == model)
        )
        similar_result = await db.execute(similar)
        similar_listings = similar_result.scalars().all()
        if similar_listings:
            stats = await calculate_market_stats(similar_listings)

        for vid in vehicle_ids:
            v_listings = listings_by_vehicle.get(vid, [])
            if not v_listings:
                continue

            v_listings.sort(key=lambda x: x.current_price)
            main_listing = v_listings[0]

            alt_list = [
                {
                    "source": l.source,
                    "url": l.url,
                    "price": l.current_price,
                }
                for l in v_listings
            ]

            days_published = 0
            if main_listing.date_found:
                if main_listing.date_found.tzinfo is None:
                    now = datetime.now()
                else:
                    now = datetime.now(timezone.utc)
                days_published = (now - main_listing.date_found).days

            mileage = main_listing.vehicle.mileage if main_listing.vehicle else None
            year = main_listing.vehicle.year if main_listing.vehicle else 0

            score = calculate_score(
                price=main_listing.current_price,
                market_avg=stats["avg"],
                mileage=mileage,
                year=year,
                days_published=days_published,
            )

            items.append(
                ListingWithScore(
                    id=main_listing.id,
                    vehicle_id=main_listing.vehicle_id,
                    source=main_listing.source,
                    url=main_listing.url,
                    current_price=main_listing.current_price,
                    currency=main_listing.currency,
                    date_found=main_listing.date_found,
                    date_updated=main_listing.date_updated,
                    is_active=main_listing.is_active,
                    vehicle=main_listing.vehicle,
                    opportunity_score=score["score"],
                    score_label=score["label"],
                    alternative_listings=alt_list,
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
