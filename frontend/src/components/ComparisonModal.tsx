"use client";

import type { ListingWithScore } from "@/types";

interface ComparisonModalProps {
  listings: ListingWithScore[];
  onClose: () => void;
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

export default function ComparisonModal({ listings, onClose }: ComparisonModalProps) {
  const minPrice = Math.min(...listings.map((l) => l.current_price));
  const minMileage = Math.min(...listings.map((l) => l.vehicle?.mileage ?? Infinity));
  const maxYear = Math.max(...listings.map((l) => l.vehicle?.year ?? 0));

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center overflow-y-auto bg-black/70 p-4">
      <div className="w-full max-w-5xl rounded-xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-2xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-bold">Comparar vehiculos</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-[var(--muted)] transition-colors hover:bg-[var(--secondary)] hover:text-[var(--foreground)]"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="w-36 py-3 pr-4 text-left text-xs font-medium text-[var(--muted)]"></th>
                {listings.map((l) => (
                  <th key={l.id} className="px-3 py-3 text-left">
                    <div className="flex items-center gap-2">
                      {(l.opportunity_score ?? 0) >= 80 && (
                        <svg className="h-4 w-4 text-yellow-500" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                      )}
                      <span className="font-semibold">
                        {l.vehicle?.brand} {l.vehicle?.model}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Precio</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    <div className="flex items-center gap-1.5">
                      <span className={l.current_price === minPrice ? "font-bold text-emerald-500" : ""}>
                        {formatPrice(l.current_price)}
                      </span>
                      {l.current_price === minPrice && (
                        <svg className="h-4 w-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>
                      )}
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Kilometraje</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    <div className="flex items-center gap-1.5">
                      <svg className="h-3.5 w-3.5 text-[var(--muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"/><path d="M12 12l3-4"/><path d="M12 12l-2-1.5"/></svg>
                      <span className={l.vehicle?.mileage === minMileage ? "font-bold text-emerald-500" : ""}>
                        {l.vehicle?.mileage ? formatMileage(l.vehicle.mileage) : "N/A"}
                      </span>
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Ano</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    <div className="flex items-center gap-1.5">
                      <svg className="h-3.5 w-3.5 text-[var(--muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                      <span className={l.vehicle?.year === maxYear ? "font-bold text-emerald-500" : ""}>
                        {l.vehicle?.year || "N/A"}
                      </span>
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Ciudad</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    <div className="flex items-center gap-1.5">
                      <svg className="h-3.5 w-3.5 text-[var(--muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                      {l.vehicle?.city || "N/A"}
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Combustible</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    {l.vehicle?.fuel_type || "N/A"}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Transmision</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    {l.vehicle?.transmission || "N/A"}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Oportunidad</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    {l.opportunity_score !== undefined ? (
                      <div className="flex items-center gap-1.5">
                        <span
                          className={
                            l.opportunity_score >= 80
                              ? "font-bold text-yellow-500"
                              : l.opportunity_score >= 60
                                ? "text-blue-400"
                                : l.opportunity_score >= 40
                                  ? "text-yellow-400"
                                  : "text-red-400"
                          }
                        >
                          {l.opportunity_score}/100
                        </span>
                        {(l.opportunity_score ?? 0) >= 80 && (
                          <svg className="h-3.5 w-3.5 text-yellow-500" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                        )}
                      </div>
                    ) : (
                      "N/A"
                    )}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 pr-4 text-xs text-[var(--muted)]">Fuente</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-3 py-3">
                    <a
                      href={l.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--primary)] underline-offset-2 hover:underline"
                    >
                      {l.source}
                    </a>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
