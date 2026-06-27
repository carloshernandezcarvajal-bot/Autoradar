from datetime import datetime
from pydantic import BaseModel, EmailStr


class VehicleOut(BaseModel):
    id: int
    brand: str
    model: str
    version: str | None = None
    year: int
    mileage: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    color: str | None = None
    city: str | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class ListingOut(BaseModel):
    id: int
    vehicle_id: int
    source: str
    url: str
    current_price: float
    currency: str
    date_found: datetime
    date_updated: datetime
    is_active: bool
    vehicle: VehicleOut | None = None

    model_config = {"from_attributes": True}


class ListingWithScore(ListingOut):
    opportunity_score: float | None = None
    score_label: str | None = None


class PriceHistoryPoint(BaseModel):
    date: datetime
    price: float

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AlertCreate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    mileage_max: int | None = None


class AlertOut(BaseModel):
    id: int
    user_id: int
    brand: str | None = None
    model: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    mileage_max: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class FavoriteCreate(BaseModel):
    listing_id: int


class FavoriteOut(BaseModel):
    id: int
    user_id: int
    listing_id: int

    model_config = {"from_attributes": True}


class SearchParams(BaseModel):
    q: str | None = None
    brand: str | None = None
    model: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    mileage_max: int | None = None
    sort_by: str = "opportunity_score"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20
