"use client";

import { useState, useEffect } from "react";
import { Bell, Plus, Trash2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import { api } from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [priceMax, setPriceMax] = useState("");

  const loadAlerts = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getAlerts()
      .then(setAlerts)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createAlert({
        brand: brand || undefined,
        model: model || undefined,
        price_max: priceMax ? Number(priceMax) : undefined,
      } as any);
      setShowForm(false);
      setBrand("");
      setModel("");
      setPriceMax("");
      loadAlerts();
    } catch {
      // ignore
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteAlert(id);
      loadAlerts();
    } catch {
      // ignore
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Bell className="h-6 w-6 text-[var(--primary)]" />
            Mis Alertas
          </h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
          >
            <Plus className="h-4 w-4" /> Nueva alerta
          </button>
        </div>

        {showForm && (
          <form
            onSubmit={handleCreate}
            className="mb-6 rounded-lg border border-[var(--border)] bg-[var(--card)] p-4"
          >
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <input
                placeholder="Marca"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                className="rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              />
              <input
                placeholder="Modelo"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              />
              <input
                type="number"
                placeholder="Precio maximo"
                value={priceMax}
                onChange={(e) => setPriceMax(e.target.value)}
                className="rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
              />
            </div>
            <button
              type="submit"
              className="mt-3 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:opacity-90"
            >
              Crear alerta
            </button>
          </form>
        )}

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--primary)] border-t-transparent" />
          </div>
        ) : alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-[var(--muted)]">
            <Bell className="mb-4 h-12 w-12" />
            <p className="text-lg">No tienes alertas</p>
            <p className="mt-1 text-sm">
              Crea alertas para recibir notificaciones de nuevos vehiculos
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {alerts.map((alert: any) => (
              <div
                key={alert.id}
                className="flex items-center justify-between rounded-lg border border-[var(--border)] bg-[var(--card)] p-4"
              >
                <div>
                  <p className="font-medium">
                    {alert.brand || "Cualquier marca"}{" "}
                    {alert.model || "Cualquier modelo"}
                  </p>
                  <p className="text-sm text-[var(--muted)]">
                    {alert.price_max
                      ? `Max $${new Intl.NumberFormat("es-CO").format(alert.price_max)}`
                      : "Sin limite de precio"}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(alert.id)}
                  className="text-[var(--muted)] hover:text-red-400"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
