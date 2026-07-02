"use client";

import { ChevronLeft, ChevronRight, TrendingUp, BarChart3 } from "lucide-react";
import VehicleCard from "./VehicleCard";
import type { SearchResult } from "@/lib/api";

interface ResultsGridProps {
  result: SearchResult | null;
  loading: boolean;
  onPageChange: (page: number) => void;
  onFavorite?: (id: number) => void;
  favorites?: Set<number>;
  compareIds?: Set<number>;
  onCompare?: (id: number) => void;
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(price);
}

export default function ResultsGrid({
  result,
  loading,
  onPageChange,
  onFavorite,
  favorites,
  compareIds,
  onCompare,
}: ResultsGridProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--primary)] border-t-transparent" />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-[var(--muted)]">
        <TrendingUp className="mb-4 h-12 w-12" />
        <p className="text-lg">Busca vehiculos para ver resultados</p>
        <p className="mt-1 text-sm">
          Usa el buscador para encontrar oportunidades
        </p>
      </div>
    );
  }

  if (result.items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-[var(--muted)]">
        <BarChart3 className="mb-4 h-12 w-12" />
        <p className="text-lg">Sin resultados</p>
        <p className="mt-1 text-sm">Prueba con otros filtros</p>
      </div>
    );
  }

  return (
    <div>
      {result.market_stats.count > 0 && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3">
            <p className="text-xs text-[var(--muted)]">Precio promedio</p>
            <p className="mt-1 text-sm font-semibold">
              {formatPrice(result.market_stats.avg)}
            </p>
          </div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3">
            <p className="text-xs text-[var(--muted)]">Mediana</p>
            <p className="mt-1 text-sm font-semibold">
              {formatPrice(result.market_stats.median)}
            </p>
          </div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3">
            <p className="text-xs text-[var(--muted)]">Mas economicos (25%)</p>
            <p className="mt-1 text-sm font-semibold">
              {formatPrice(result.market_stats.p25)}
            </p>
          </div>
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3">
            <p className="text-xs text-[var(--muted)]">Anuncios activos</p>
            <p className="mt-1 text-sm font-semibold">
              {result.market_stats.count}
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {result.items.map((listing) => (
          <VehicleCard
            key={listing.id}
            listing={listing}
            onFavorite={onFavorite}
            isFavorite={favorites?.has(listing.id)}
            onCompare={onCompare}
            isCompared={compareIds?.has(listing.id)}
          />
        ))}
      </div>
    </div>
  );
}
