"use client";

import { useState, useEffect } from "react";
import { Heart } from "lucide-react";
import Navbar from "@/components/Navbar";
import VehicleCard from "@/components/VehicleCard";
import { api } from "@/lib/api";

export default function FavoritesPage() {
  const [listings, setListings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getFavorites()
      .then(setListings)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-bold flex items-center gap-2">
          <Heart className="h-6 w-6 text-red-400" />
          Mis Favoritos
        </h1>
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--primary)] border-t-transparent" />
          </div>
        ) : listings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-[var(--muted)]">
            <Heart className="mb-4 h-12 w-12" />
            <p className="text-lg">No tienes favoritos</p>
            <p className="mt-1 text-sm">Agrega vehiculos desde la busqueda</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {listings.map((listing: any) => (
              <VehicleCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
