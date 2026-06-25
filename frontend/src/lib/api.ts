const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Error de red" }));
    throw new Error(error.detail || `Error ${res.status}`);
  }

  return res.json();
}

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

export interface SearchResult {
  items: ListingWithScore[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  market_stats: {
    avg: number;
    median: number;
    p25: number;
    p75: number;
    count: number;
  };
}

export interface Alert {
  id: number;
  user_id: number;
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

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const api = {
  search: (params: Record<string, unknown> | { q?: string; brand?: string; model?: string; year_min?: number; year_max?: number; price_min?: number; price_max?: number; mileage_max?: number; sort_by?: string; sort_order?: string; page?: number; page_size?: number }) =>
    fetchApi<SearchResult>("/api/search", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  getVehicle: (id: number) => fetchApi<ListingWithScore>(`/api/vehicles/${id}`),

  getPriceHistory: (id: number) =>
    fetchApi<{ date: string; price: number }[]>(
      `/api/vehicles/${id}/price-history`
    ),

  getBrands: () => fetchApi<string[]>("/api/vehicles/brands/list"),

  getModels: (brand?: string) =>
    fetchApi<string[]>(
      `/api/vehicles/models/list${brand ? `?brand=${brand}` : ""}`
    ),

  register: (email: string, password: string) =>
    fetchApi<User>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    fetchApi<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getMe: () => fetchApi<User>("/api/auth/me"),

  getAlerts: () => fetchApi<Alert[]>("/api/alerts"),

  createAlert: (data: Partial<Alert>) =>
    fetchApi<Alert>("/api/alerts", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteAlert: (id: number) =>
    fetchApi<{ ok: boolean }>(`/api/alerts/${id}`, { method: "DELETE" }),

  getFavorites: () => fetchApi<Listing[]>("/api/favorites"),

  addFavorite: (listingId: number) =>
    fetchApi<{ id: number }>("/api/favorites", {
      method: "POST",
      body: JSON.stringify({ listing_id: listingId }),
    }),

  removeFavorite: (listingId: number) =>
    fetchApi<{ ok: boolean }>(`/api/favorites/${listingId}`, {
      method: "DELETE",
    }),

  health: () => fetchApi<{ status: string }>("/api/health"),
};
