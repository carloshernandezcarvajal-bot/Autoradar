"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { TrendingUp, Zap, Shield, BarChart3, ChevronRight } from "lucide-react";
import Navbar from "@/components/Navbar";
import SearchBar from "@/components/SearchBar";
import ResultsGrid from "@/components/ResultsGrid";
import ComparisonModal from "@/components/ComparisonModal";
import { api } from "@/lib/api";
import type { SearchFilters } from "@/types";
import type { SearchResult } from "@/lib/api";

export default function Home() {
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [favorites, setFavorites] = useState<Set<number>>(new Set());
  const [showSearch, setShowSearch] = useState(false);
  const [compareIds, setCompareIds] = useState<Set<number>>(new Set());
  const [showCompare, setShowCompare] = useState(false);

  // Estados y refs para scroll infinito
  const [currentFilters, setCurrentFilters] = useState<SearchFilters | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const observerTarget = useRef<HTMLDivElement>(null);

  const handleSearch = async (filters: SearchFilters, isLoadMore = false) => {
    if (isLoadMore) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    try {
      const data = await api.search(filters);
      if (isLoadMore) {
        setResult((prev) => {
          if (!prev) return data;
          return {
            ...data,
            items: [...prev.items, ...data.items],
          };
        });
      } else {
        setResult(data);
      }
      setCurrentFilters(filters);
    } catch {
      if (!isLoadMore) {
        setResult(null);
        setCurrentFilters(null);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleCompare = (id: number) => {
    setCompareIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < 4) {
        next.add(id);
      }
      return next;
    });
  };

  const handleFavorite = (id: number) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // Cargar más paginas de forma asíncrona al scrolear
  const handleLoadMore = useCallback(() => {
    if (loading || loadingMore || !result || !currentFilters) return;
    if (result.page >= result.total_pages) return;

    const nextPage = result.page + 1;
    handleSearch({ ...currentFilters, page: nextPage }, true);
  }, [loading, loadingMore, result, currentFilters]);

  // Observer al final del grid de resultados
  useEffect(() => {
    const target = observerTarget.current;
    if (!target || !result || result.page >= result.total_pages) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          handleLoadMore();
        }
      },
      { threshold: 0.1, rootMargin: "150px" } // Precargar un poco antes de que toque el fondo de pantalla
    );

    observer.observe(target);
    return () => {
      observer.unobserve(target);
    };
  }, [result, handleLoadMore]);

  return (
    <div className="min-h-screen">
      <Navbar onSearchToggle={() => setShowSearch(!showSearch)} />

      <main>
        <section className="relative overflow-hidden border-b border-[var(--border)]">
          <div className="absolute inset-0 bg-gradient-to-b from-[var(--primary)]/5 to-transparent" />
          <div className="relative mx-auto max-w-7xl px-4 py-16 sm:py-24">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                Encuentra tu{" "}
                <span className="text-[var(--primary)]">proximo carro</span>{" "}
                con inteligencia
              </h1>
              <p className="mx-auto mt-4 max-w-2xl text-lg text-[var(--muted)]">
                Compara precios, analiza el mercado y descubre oportunidades
                reales en vehiculos usados en Colombia.
              </p>
            </div>

            <div className="mx-auto mt-8 max-w-3xl">
              <SearchBar onSearch={handleSearch} />
            </div>

            <div className="mx-auto mt-12 grid max-w-4xl grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                {
                  icon: TrendingUp,
                  label: "Historial de precios",
                  desc: "Evolucion del precio",
                },
                {
                  icon: Zap,
                  label: "Indice de oportunidad",
                  desc: "Score 0-100",
                },
                {
                  icon: Shield,
                  label: "Alertas inteligentes",
                  desc: "Notificaciones",
                },
                {
                  icon: BarChart3,
                  label: "Estadisticas",
                  desc: "Analisis de mercado",
                },
              ].map(({ icon: Icon, label, desc }) => (
                <div
                  key={label}
                  className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 text-center transition-colors hover:border-[var(--primary)]/30"
                >
                  <Icon className="mx-auto h-5 w-5 text-[var(--primary)]" />
                  <p className="mt-2 text-sm font-medium">{label}</p>
                  <p className="mt-0.5 text-xs text-[var(--muted)]">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-8">
          {compareIds.size >= 2 && (
            <div className="mb-4 flex items-center justify-between rounded-lg border border-[var(--primary)]/30 bg-[var(--primary)]/5 px-4 py-3">
              <p className="text-sm">
                <span className="font-semibold">{compareIds.size}</span> vehiculos seleccionados para comparar
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => { setCompareIds(new Set()); setShowCompare(false); }}
                  className="text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
                >
                  Limpiar
                </button>
                <button
                  onClick={() => setShowCompare(true)}
                  className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
                >
                  Comparar
                </button>
              </div>
            </div>
          )}
          <ResultsGrid
            result={result}
            loading={loading}
            onPageChange={() => {}}
            onFavorite={handleFavorite}
            favorites={favorites}
            compareIds={compareIds}
            onCompare={handleCompare}
          />

          {/* Observer Target / Spinner de Carga de Scroll Infinito */}
          {result && result.page < result.total_pages && (
            <div ref={observerTarget} className="mt-10 flex items-center justify-center py-6">
              {loadingMore ? (
                <div className="flex items-center gap-2.5 text-sm text-[var(--muted)]">
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--primary)] border-t-transparent" />
                  <span className="font-medium animate-pulse">Cargando más vehículos...</span>
                </div>
              ) : (
                <div className="h-1.5 w-1.5 rounded-full bg-[var(--border)]" />
              )}
            </div>
          )}
        </section>

        {showCompare && result && compareIds.size >= 2 && (
          <ComparisonModal
            listings={result.items.filter((l) => compareIds.has(l.id))}
            onClose={() => setShowCompare(false)}
          />
        )}

        {!result && (
          <section className="mx-auto max-w-7xl px-4 py-12">
            <h2 className="mb-6 text-2xl font-bold text-center">
              Marcas populares
            </h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6">
              {["Chevrolet", "Mazda", "Renault", "Toyota", "Nissan", "Hyundai"].map(
                (brand) => (
                  <button
                    key={brand}
                    onClick={() => handleSearch({ brand, page: 1, page_size: 20 })}
                    className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 text-center transition-all hover:border-[var(--primary)]/50 hover:shadow-lg"
                  >
                    <p className="font-medium">{brand}</p>
                    <ChevronRight className="mx-auto mt-1 h-4 w-4 text-[var(--muted)]" />
                  </button>
                )
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-[var(--border)] py-8 text-center text-sm text-[var(--muted)]">
        <p>Autoradar &copy; {new Date().getFullYear()} - Comparador inteligente de vehiculos en Colombia</p>
      </footer>
    </div>
  );
}
