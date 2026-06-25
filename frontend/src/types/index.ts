export interface Vehicle {
  id: number;
  brand: string;
  model: string;
  version?: string;
  year: number;
  mileage?: number;
  fuel_type?: string;
  transmission?: string;
  color?: string;
  city?: string;
  image_url?: string;
}

export interface Listing {
  id: number;
  vehicle_id: number;
  source: string;
  url: string;
  current_price: number;
  currency: string;
  date_found: string;
  date_updated: string;
  is_active: boolean;
  vehicle?: Vehicle;
}

export interface ListingWithScore extends Listing {
  opportunity_score?: number;
  score_label?: string;
}

export interface SearchFilters {
  q?: string;
  brand?: string;
  model?: string;
  year_min?: number;
  year_max?: number;
  price_min?: number;
  price_max?: number;
  mileage_max?: number;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}

export interface Alert {
  id: number;
  brand?: string;
  model?: string;
  year_min?: number;
  year_max?: number;
  price_min?: number;
  price_max?: number;
  mileage_max?: number;
  is_active: boolean;
}

export interface User {
  id: number;
  email: string;
}
