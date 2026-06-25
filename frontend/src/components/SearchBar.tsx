"use client";

import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { api } from "@/lib/api";
import type { SearchFilters } from "@/types";

interface SearchBarProps {
  onSearch: (filters: SearchFilters) => void;
  initialFilters?: SearchFilters;
}

export default function SearchBar({ onSearch, initialFilters }: SearchBarProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [brands, setBrands] = useState<string[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [filters, setFilters] = useState<SearchFilters>(
    initialFilters || { q: "", page: 1, page_size: 20 }
  );

  useEffect(() => {
    api.getBrands().then(setBrands).catch(() => {});
  }, []);

  useEffect(() => {
    if (filters.brand) {
      api.getModels(filters.brand).then(setModels).catch(() => {});
    } else {
      setModels([]);
    }
  }, [filters.brand]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  const clearFilters = () => {
    const cleared: SearchFilters = { q: "", page: 1, page_size: 20 };
    setFilters(cleared);
    onSearch(cleared);
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" />
          <input
            type="text"
            placeholder="Buscar marca, modelo..."
            value={filters.q || ""}
            onChange={(e) => setFilters({ ...filters, q: e.target.value })}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-[var(--primary)]"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm transition-colors ${
            showFilters
              ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
              : "border-[var(--border)] hover:bg-[var(--secondary)]"
          }`}
        >
          <SlidersHorizontal className="h-4 w-4" />
          Filtros
        </button>
        <button
          type="submit"
          className="rounded-lg bg-[var(--primary)] px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
        >
          Buscar
        </button>
      </form>

      {showFilters && (
        <div className="mt-4 rounded-lg border border-[var(--border)] bg-[var(--card)] p-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="mb-1 block text-xs text-[var(--muted)]">
                Marca
              </label>
              <select
                value={filters.brand || ""}
                onChange={(e) =>
                  setFilters({ ...filters, brand: e.target.value || undefined })
                }
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              >
                <option value="">Todas</option>
                {brands.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--muted)]">
                Modelo
              </label>
              <select
                value={filters.model || ""}
                onChange={(e) =>
                  setFilters({ ...filters, model: e.target.value || undefined })
                }
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              >
                <option value="">Todos</option>
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--muted)]">
                Ano minimo
              </label>
              <input
                type="number"
                placeholder="Ej: 2018"
                value={filters.year_min || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    year_min: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--muted)]">
                Precio maximo
              </label>
              <input
                type="number"
                placeholder="Ej: 50000000"
                value={filters.price_max || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    price_max: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--muted)]">
                Kilometraje maximo
              </label>
              <input
                type="number"
                placeholder="Ej: 50000"
                value={filters.mileage_max || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    mileage_max: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-[var(--muted)]">
                Ordenar por
              </label>
              <select
                value={`${filters.sort_by || "opportunity_score"}_${filters.sort_order || "desc"}`}
                onChange={(e) => {
                  const [sort_by, sort_order] = e.target.value.split("_");
                  setFilters({ ...filters, sort_by, sort_order });
                }}
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              >
                <option value="opportunity_score_desc">Mejor oportunidad</option>
                <option value="price_asc">Precio: menor a mayor</option>
                <option value="price_desc">Precio: mayor a menor</option>
                <option value="mileage_asc">Kilometraje: menor a mayor</option>
                <option value="mileage_desc">Kilometraje: mayor a menor</option>
              </select>
            </div>
          </div>
          <button
            onClick={clearFilters}
            className="mt-3 flex items-center gap-1 text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
          >
            <X className="h-3 w-3" /> Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}
