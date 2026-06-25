from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.schemas import FavoriteOut, ListingOut

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("", response_model=FavoriteOut)
async def add_favorite(
    listing_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.listing_id == listing_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya esta en favoritos")

    listing = await db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

    fav = Favorite(user_id=user.id, listing_id=listing_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@router.get("", response_model=list[ListingOut])
async def list_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.listing).selectinload(Listing.vehicle))
        .where(Favorite.user_id == user.id)
    )
    return [fav.listing for fav in result.scalars().all()]


@router.delete("/{listing_id}")
async def remove_favorite(
    listing_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.listing_id == listing_id
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    await db.delete(fav)
    await db.commit()
    return {"ok": True}
