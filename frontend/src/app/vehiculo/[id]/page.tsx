"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Heart,
  Calendar,
  Gauge,
  MapPin,
  ExternalLink,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Info,
  Car,
  Compass,
  AlertCircle
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { api, type ListingWithScore } from "@/lib/api";

interface PricePoint {
  date: string;
  price: number;
}

export default function VehicleDetailPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const listingId = parseInt(id);

  const [listing, setListing] = useState<ListingWithScore | null>(null);
  const [history, setHistory] = useState<PricePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);

  // Tooltip state for SVG chart
  const [hoveredPoint, setHoveredPoint] = useState<{
    x: number;
    y: number;
    price: number;
    date: string;
  } | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch vehicle details and price history
        const vehicleData = await api.getVehicle(listingId);
        setListing(vehicleData);

        const historyData = await api.getPriceHistory(listingId);
        // Ensure price history points are sorted by date
        const sortedHistory = [...historyData].sort(
          (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
        );
        setHistory(sortedHistory);

        // Check if favorite
        try {
          const favs = await api.getFavorites();
          setIsFavorite(favs.some((fav) => fav.id === listingId));
        } catch {
          // Ignore auth errors for favorites
        }
      } catch (err: unknown) {
        console.error(err);
        setError("No se pudo cargar la información del vehículo.");
      } finally {
        setLoading(false);
      }
    }

    if (listingId) {
      loadData();
    }
  }, [listingId]);

  const toggleFavorite = async () => {
    if (!listing) return;
    setFavoriteLoading(true);
    try {
      if (isFavorite) {
        await api.removeFavorite(listingId);
        setIsFavorite(false);
      } else {
        await api.addFavorite(listingId);
        setIsFavorite(true);
      }
    } catch (err: unknown) {
      alert("Debes iniciar sesión para agregar a favoritos.");
    } finally {
      setFavoriteLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="flex h-[60vh] flex-col items-center justify-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--primary)] border-t-transparent"></div>
          <p className="text-[var(--muted)]">Cargando análisis de vehículo...</p>
        </div>
      </div>
    );
  }

  if (error || !listing) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="mx-auto max-w-xl px-4 py-20 text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
          <h2 className="mt-4 text-2xl font-bold">Vehículo no encontrado</h2>
          <p className="mt-2 text-[var(--muted)]">{error || "La publicación no existe o fue eliminada."}</p>
          <Link
            href="/"
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
          >
            <ArrowLeft className="h-4 w-4" /> Volver al buscador
          </Link>
        </div>
      </div>
    );
  }

  const vehicle = listing.vehicle;
  const score = listing.opportunity_score ?? 50;
  const label = listing.score_label ?? "Precio normal";

  // Helper for pricing formatting
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatMileage = (km: number) => {
    return new Intl.NumberFormat("es-CO").format(km) + " km";
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("es-CO", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  };

  // Score UI Helpers
  const getScoreColors = (val: number) => {
    if (val >= 80) return { stroke: "stroke-emerald-500", text: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" };
    if (val >= 60) return { stroke: "stroke-blue-500", text: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" };
    if (val >= 40) return { stroke: "stroke-yellow-500", text: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/20" };
    return { stroke: "stroke-red-500", text: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20" };
  };

  const scoreColors = getScoreColors(score);
  const radius = 50;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Price analysis
  const initialPrice = history.length > 0 ? history[0].price : listing.current_price;
  const priceDiff = listing.current_price - initialPrice;
  const hasPriceDrop = priceDiff < 0;

  // Custom SVG chart calculations
  const svgWidth = 500;
  const svgHeight = 250;
  const paddingLeft = 65;
  const paddingRight = 25;
  const paddingTop = 20;
  const paddingBottom = 40;

  const chartWidth = svgWidth - paddingLeft - paddingRight;
  const chartHeight = svgHeight - paddingTop - paddingBottom;

  let points: { x: number; y: number; price: number; date: string }[] = [];
  let yAxisLabels: number[] = [];

  if (history.length >= 2) {
    const prices = history.map((h) => h.price);
    const maxP = Math.max(...prices);
    const minP = Math.min(...prices);
    const rangeP = maxP - minP;

    // Buffers to avoid drawing line on coordinates 0 or height bounds
    const minYVal = rangeP === 0 ? minP * 0.95 : minP - rangeP * 0.15;
    const maxYVal = rangeP === 0 ? maxP * 1.05 : maxP + rangeP * 0.15;
    const rangeY = maxYVal - minYVal;

    const timestamps = history.map((h) => new Date(h.date).getTime());
    const minT = Math.min(...timestamps);
    const maxT = Math.max(...timestamps);
    const rangeT = maxT - minT;

    points = history.map((h) => {
      const t = new Date(h.date).getTime();
      const x = paddingLeft + ((t - minT) / (rangeT || 1)) * chartWidth;
      const y = paddingTop + chartHeight - ((h.price - minYVal) / (rangeY || 1)) * chartHeight;
      return { x, y, price: h.price, date: h.date };
    });

    // Generate 4 nicely distributed labels for Y-axis
    for (let i = 0; i < 4; i++) {
      yAxisLabels.push(minYVal + (rangeY / 3) * i);
    }
  }

  // Find nearest point for interactive tooltip on SVG mouse move
  const handleSvgMouseMove = (e: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
    if (points.length < 2) return;
    const svgRect = e.currentTarget.getBoundingClientRect();
    const mouseX = e.clientX - svgRect.left;
    
    // Scale factor if SVG container is scaled by CSS
    const scaleX = svgWidth / svgRect.width;
    const scaledMouseX = mouseX * scaleX;

    // Find closest point by x coordinate
    let closest = points[0];
    let minDist = Math.abs(points[0].x - scaledMouseX);

    for (let i = 1; i < points.length; i++) {
      const dist = Math.abs(points[i].x - scaledMouseX);
      if (dist < minDist) {
        minDist = dist;
        closest = points[i];
      }
    }

    setHoveredPoint(closest);
  };

  return (
    <div className="min-h-screen pb-12">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-8">
        {/* Navigation Header */}
        <div className="mb-8 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
          >
            <ArrowLeft className="h-4 w-4" /> Volver al buscador
          </Link>

          <button
            onClick={toggleFavorite}
            disabled={favoriteLoading}
            className={`flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm font-medium transition-all hover:bg-[var(--secondary)] ${
              isFavorite ? "border-red-500/30 text-red-400" : "text-[var(--muted)] hover:text-[var(--foreground)]"
            }`}
          >
            <Heart className="h-4 w-4" fill={isFavorite ? "currentColor" : "none"} />
            {isFavorite ? "Favorito" : "Guardar favorito"}
          </button>
        </div>

        {/* Title Block */}
        <div className="mb-8">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold sm:text-4xl">
              {vehicle?.brand} {vehicle?.model}
            </h1>
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider ${
                listing.is_active
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-red-500/10 text-red-400 border border-red-500/20"
              }`}
            >
              {listing.is_active ? "Activo" : "Inactivo / Vendido"}
            </span>
          </div>
          {vehicle?.version && (
            <p className="mt-1 text-lg text-[var(--muted)]">{vehicle.version}</p>
          )}
        </div>

        {/* Grid Layout */}
        <div className="grid gap-8 lg:grid-cols-3">
          
          {/* LEFT COLUMN: Vehicle Details & Ficha Técnica */}
          <div className="space-y-8 lg:col-span-2">
            
            {/* Mock Image / Visual Accent Card */}
            <div className="relative flex h-64 w-full flex-col items-center justify-center rounded-2xl border border-[var(--border)] bg-gradient-to-br from-[var(--secondary)] to-[var(--background)] p-8 text-center sm:h-96">
              <div className="absolute inset-0 bg-radial-gradient from-transparent to-[var(--background)]/30 opacity-50" />
              <Car className="h-20 w-20 text-[var(--primary)]/30" />
              <h2 className="mt-4 text-xl font-bold">{vehicle?.brand} {vehicle?.model}</h2>
              <p className="mt-1 max-w-sm text-xs text-[var(--muted)]">
                Las fotos originales de esta publicación están hospedadas en la plataforma de {listing.source}. Puedes verlas en el enlace original.
              </p>
              <a
                href={listing.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 flex items-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition-all hover:bg-[var(--primary-hover)] hover:shadow-lg hover:shadow-[var(--primary)]/10"
              >
                Ver publicación en {listing.source}
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>

            {/* Ficha Técnica Card */}
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
              <h3 className="mb-6 flex items-center gap-2 text-xl font-bold">
                <Compass className="h-5 w-5 text-[var(--primary)]" />
                Especificaciones del vehículo
              </h3>
              
              <div className="grid grid-cols-2 gap-6 sm:grid-cols-3">
                {[
                  { icon: Calendar, label: "Año modelo", value: vehicle?.year },
                  { icon: Gauge, label: "Kilometraje", value: vehicle?.mileage ? formatMileage(vehicle.mileage) : "No especificado" },
                  { icon: MapPin, label: "Ubicación", value: vehicle?.city || "No especificada" },
                  { icon: Car, label: "Transmisión", value: vehicle?.transmission || "No especificada" },
                  { icon: Info, label: "Combustible", value: vehicle?.fuel_type || "No especificado" },
                  { icon: Sparkles, label: "Color exterior", value: vehicle?.color || "No especificado" }
                ].map((item, idx) => (
                  <div key={idx} className="flex flex-col gap-1 rounded-xl border border-[var(--border)] bg-[var(--background)]/50 p-4 transition-colors hover:border-[var(--primary)]/20">
                    <item.icon className="h-5 w-5 text-[var(--muted)]" />
                    <span className="mt-2 text-xs font-semibold text-[var(--muted)] uppercase tracking-wider">{item.label}</span>
                    <span className="text-sm font-bold text-[var(--foreground)]">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Price Card, Opportunity Score, Price History */}
          <div className="space-y-8">
            
            {/* Price Overview Card */}
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-xl">
              <span className="text-xs font-bold text-[var(--muted)] uppercase tracking-wider">Precio de publicación</span>
              <div className="mt-1 flex items-baseline gap-2">
                <h2 className="text-3xl font-black text-[var(--foreground)]">{formatPrice(listing.current_price)}</h2>
                <span className="text-sm font-semibold text-[var(--muted)]">{listing.currency}</span>
              </div>
              
              <div className="mt-4 flex items-center gap-3 border-t border-[var(--border)] pt-4">
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${hasPriceDrop ? "bg-emerald-500/10 text-emerald-400" : "bg-[var(--border)] text-[var(--muted)]"}`}>
                  {hasPriceDrop ? <TrendingDown className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />}
                </div>
                <div>
                  <p className="text-xs text-[var(--muted)]">Historial de cambio de precio</p>
                  <p className={`text-xs font-bold ${hasPriceDrop ? "text-emerald-400" : "text-[var(--muted)]"}`}>
                    {priceDiff === 0 
                      ? "Sin variación desde el registro" 
                      : `${hasPriceDrop ? "Bajó" : "Subió"} ${formatPrice(Math.abs(priceDiff))}`}
                  </p>
                </div>
              </div>
            </div>

            {/* Opportunity Score Card */}
            <div className={`rounded-2xl border ${scoreColors.border} ${scoreColors.bg} p-6 transition-all`}>
              <h3 className="mb-4 text-lg font-bold">Índice de oportunidad</h3>
              
              <div className="flex items-center gap-6">
                {/* SVG Radial Gauge */}
                <div className="relative h-28 w-28 flex-shrink-0">
                  <svg className="h-full w-full -rotate-90">
                    {/* Background Circle */}
                    <circle
                      cx="56"
                      cy="56"
                      r={radius}
                      className="stroke-[var(--border)]"
                      strokeWidth={strokeWidth}
                      fill="transparent"
                    />
                    {/* Animated Fill Circle */}
                    <circle
                      cx="56"
                      cy="56"
                      r={radius}
                      className={`${scoreColors.stroke} transition-all duration-1000 ease-out`}
                      strokeWidth={strokeWidth}
                      fill="transparent"
                      strokeDasharray={circumference}
                      strokeDashoffset={strokeDashoffset}
                      strokeLinecap="round"
                    />
                  </svg>
                  {/* Score text in center */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-black">{score}</span>
                    <span className="text-[10px] uppercase font-bold text-[var(--muted)]">Score</span>
                  </div>
                </div>

                <div>
                  <span className={`text-sm font-bold ${scoreColors.text}`}>
                    {label}
                  </span>
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    Calculado en base a la relación de precio actual frente al promedio del mercado de su modelo, año, kilometraje y tiempo publicado.
                  </p>
                </div>
              </div>
            </div>

            {/* Price History Chart Card */}
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
              <h3 className="mb-4 text-lg font-bold">Historial de precios</h3>
              
              {history.length < 2 ? (
                <div className="flex h-44 flex-col items-center justify-center rounded-xl border border-dashed border-[var(--border)] p-4 text-center">
                  <Info className="h-6 w-6 text-[var(--muted)]" />
                  <p className="mt-2 text-xs text-[var(--muted)]">
                    No hay cambios de precio registrados.
                  </p>
                  <p className="mt-0.5 text-[10px] text-[var(--muted)]">
                    Monitorearemos esta publicación y registraremos cualquier cambio.
                  </p>
                </div>
              ) : (
                <div className="relative">
                  {/* SVG Line Chart */}
                  <svg
                    width="100%"
                    height={svgHeight}
                    viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                    className="overflow-visible"
                    onMouseMove={handleSvgMouseMove}
                    onMouseLeave={() => setHoveredPoint(null)}
                  >
                    {/* Y-Axis Gridlines */}
                    {yAxisLabels.map((val, idx) => {
                      const y = paddingTop + chartHeight - (idx / 3) * chartHeight;
                      return (
                        <g key={idx} className="opacity-30">
                          <line
                            x1={paddingLeft}
                            y1={y}
                            x2={svgWidth - paddingRight}
                            y2={y}
                            className="stroke-[var(--border)]"
                            strokeDasharray="4 4"
                          />
                          <text
                            x={paddingLeft - 8}
                            y={y + 4}
                            textAnchor="end"
                            className="fill-[var(--muted)] text-[10px]"
                          >
                            {(val / 1000000).toFixed(0)}M
                          </text>
                        </g>
                      );
                    })}

                    {/* Area under line */}
                    {points.length > 0 && (
                      <path
                        d={`M ${points[0].x} ${paddingTop + chartHeight} 
                           L ${points.map((p) => `${p.x} ${p.y}`).join(" L ")} 
                           L ${points[points.length - 1].x} ${paddingTop + chartHeight} Z`}
                        className="fill-[var(--primary)]/10"
                      />
                    )}

                    {/* Line path */}
                    {points.length > 0 && (
                      <path
                        d={`M ${points.map((p) => `${p.x} ${p.y}`).join(" L ")}`}
                        fill="none"
                        className="stroke-[var(--primary)]"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    )}

                    {/* Interactive dots */}
                    {points.map((p, idx) => (
                      <circle
                        key={idx}
                        cx={p.x}
                        cy={p.y}
                        r={hoveredPoint?.price === p.price && hoveredPoint?.date === p.date ? "6" : "4"}
                        className={`fill-[var(--card)] stroke-[var(--primary)] transition-all ${
                          hoveredPoint?.price === p.price && hoveredPoint?.date === p.date ? "stroke-[3px]" : "stroke-[2px]"
                        }`}
                      />
                    ))}

                    {/* Interactive Vertical Guideline */}
                    {hoveredPoint && (
                      <line
                        x1={hoveredPoint.x}
                        y1={paddingTop}
                        x2={hoveredPoint.x}
                        y2={paddingTop + chartHeight}
                        className="stroke-[var(--primary)]/30"
                        strokeDasharray="2 2"
                      />
                    )}

                    {/* X-Axis labels (First and last dates) */}
                    {points.length > 0 && (
                      <g className="opacity-70">
                        {/* First date */}
                        <text
                          x={points[0].x}
                          y={paddingTop + chartHeight + 20}
                          textAnchor="start"
                          className="fill-[var(--muted)] text-[9px] font-bold"
                        >
                          {new Date(points[0].date).toLocaleDateString("es-CO", { day: "numeric", month: "short" })}
                        </text>
                        {/* Last date */}
                        <text
                          x={points[points.length - 1].x}
                          y={paddingTop + chartHeight + 20}
                          textAnchor="end"
                          className="fill-[var(--muted)] text-[9px] font-bold"
                        >
                          {new Date(points[points.length - 1].date).toLocaleDateString("es-CO", { day: "numeric", month: "short" })}
                        </text>
                      </g>
                    )}
                  </svg>

                  {/* Tooltip Overlay */}
                  {hoveredPoint && (
                    <div className="absolute left-[70px] top-0 pointer-events-none rounded-lg border border-[var(--border)] bg-[var(--background)]/90 p-2 shadow-lg backdrop-blur-sm text-left">
                      <p className="text-[10px] text-[var(--muted)] font-semibold uppercase">{formatDate(hoveredPoint.date)}</p>
                      <p className="text-xs font-bold text-[var(--accent)]">{formatPrice(hoveredPoint.price)}</p>
                    </div>
                  )}
                </div>
              )}
            </div>

          </div>
        </div>
      </main>
      
      <footer className="mt-16 border-t border-[var(--border)] py-8 text-center text-sm text-[var(--muted)]">
        <p>Autoradar &copy; {new Date().getFullYear()} - Comparador inteligente de vehículos en Colombia</p>
      </footer>
    </div>
  );
}
