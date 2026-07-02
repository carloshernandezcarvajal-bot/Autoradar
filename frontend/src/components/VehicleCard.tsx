"use client";

import Link from "next/link";
import { Heart, MapPin, Gauge, Calendar, ExternalLink, BarChart3 } from "lucide-react";
import type { ListingWithScore } from "@/types";

interface VehicleCardProps {
  listing: ListingWithScore;
  onFavorite?: (id: number) => void;
  isFavorite?: boolean;
  onCompare?: (id: number) => void;
  isCompared?: boolean;
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(price);
}

function formatMileage(km: number): string {
  return new Intl.NumberFormat("es-CO").format(km) + " km";
}

function getScoreColor(score: number | undefined): string {
  if (!score) return "bg-[var(--muted)]";
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-blue-500";
  if (score >= 40) return "bg-yellow-500";
  return "bg-red-500";
}

function getScoreLabelColor(label: string | undefined): string {
  switch (label) {
    case "Excelente oportunidad":
      return "text-emerald-400";
    case "Buena oportunidad":
      return "text-blue-400";
    case "Precio normal":
      return "text-yellow-400";
    case "Sobrevalorado":
      return "text-red-400";
    default:
      return "text-[var(--muted)]";
  }
}

function formatSource(source: string): string {
  const s = source.toLowerCase();
  if (s === "carroya") return "CarroYa";
  if (s === "vendetunave") return "VendeTuNave";
  if (s === "tucarro") return "TuCarro";
  if (s === "segundazo") return "Segundazo";
  if (s === "listoya") return "ListoYaAutos";
  if (s === "carmax") return "CarMax";
  return source;
}

export default function VehicleCard({
  listing,
  onFavorite,
  isFavorite,
  onCompare,
  isCompared,
}: VehicleCardProps) {
  const vehicle = listing.vehicle;
  const isExcellent = (listing.opportunity_score ?? 0) >= 80;

  return (
    <div className={`group relative rounded-xl border bg-[var(--card)] p-4 transition-all hover:shadow-lg ${
      isExcellent
        ? "border-yellow-500/50 shadow-yellow-500/10 hover:border-yellow-500"
        : "border-[var(--border)] hover:border-[var(--primary)]/50 hover:shadow-[var(--primary)]/5"
    }`}>
      {isExcellent && (
        <div className="absolute -right-1 -top-1 flex items-center gap-1 rounded-bl-lg rounded-tr-xl bg-gradient-to-br from-yellow-500 to-amber-600 px-2.5 py-1 text-xs font-bold text-white shadow-lg">
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          {listing.opportunity_score}
        </div>
      )}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="truncate text-lg font-semibold">
            {vehicle?.brand} {vehicle?.model}
          </h3>
          {vehicle?.version && (
            <p className="truncate text-sm text-[var(--muted)]">
              {vehicle.version}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!isExcellent && listing.opportunity_score !== undefined && (
            <div className="flex items-center gap-1.5">
              <div
                className={`h-2 w-2 rounded-full ${getScoreColor(listing.opportunity_score)}`}
              />
              <span
                className={`text-xs font-medium ${getScoreLabelColor(listing.score_label)}`}
              >
                {listing.opportunity_score}
              </span>
            </div>
          )}
          <button
            onClick={() => onCompare?.(listing.id)}
            className={`rounded-md border px-2 py-1 text-xs transition-colors ${
              isCompared
                ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                : "border-transparent text-[var(--muted)] hover:border-[var(--border)] hover:text-[var(--foreground)]"
            }`}
          >
            {isCompared ? "Quitar" : "Comparar"}
          </button>
          <button
            onClick={() => onFavorite?.(listing.id)}
            className={`transition-colors ${
              isFavorite ? "text-red-400" : "text-[var(--muted)] hover:text-red-400"
            }`}
          >
            <Heart className="h-4 w-4" fill={isFavorite ? "currentColor" : "none"} />
          </button>
        </div>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2">
        <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
          <Calendar className="h-3.5 w-3.5" />
          {vehicle?.year}
        </div>
        <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
          <Gauge className="h-3.5 w-3.5" />
          {vehicle?.mileage ? formatMileage(vehicle.mileage) : "N/A"}
        </div>
        <div className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
          <MapPin className="h-3.5 w-3.5" />
          {vehicle?.city || "N/A"}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div>
          <p className="text-lg font-bold text-[var(--accent)]">
            {formatPrice(listing.current_price)}
          </p>
          <p className="text-xs text-[var(--muted)]">
            {formatSource(listing.source)} &middot; {listing.currency}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href={`/vehiculo/${listing.id}`}
            className="flex items-center gap-1 rounded-lg bg-[var(--primary)]/10 text-[var(--primary)] px-3 py-2 text-xs font-semibold transition-colors hover:bg-[var(--primary)]/20"
          >
            <BarChart3 className="h-3.5 w-3.5" />
            Análisis
          </Link>
          <a
            href={listing.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 rounded-lg bg-[var(--secondary)] px-3 py-2 text-xs transition-colors hover:bg-[var(--border)] text-[var(--foreground)]"
          >
            <ExternalLink className="h-3 w-3" />
            Original
          </a>
        </div>
      </div>

      {listing.alternative_listings && listing.alternative_listings.length > 1 && (
        <div className="mt-4 border-t border-[var(--border)] pt-3">
          <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--muted)] mb-2">
            Disponible en otros portales:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {listing.alternative_listings.map((alt, index) => (
              <a
                key={index}
                href={alt.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium transition-all ${
                  alt.price === listing.current_price
                    ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-400 hover:border-emerald-500"
                    : "border-[var(--border)] bg-[var(--card)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]"
                }`}
              >
                <span>{formatSource(alt.source)}</span>
                <span className="font-semibold">{formatPrice(alt.price)}</span>
                {alt.price === listing.current_price && (
                  <span className="rounded bg-emerald-500/20 px-1 py-0.2 text-[8px] font-bold text-emerald-400">
                    ¡Menor precio!
                  </span>
                )}
                <ExternalLink className="h-2.5 w-2.5 opacity-60" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
