"use client";

import { useState } from "react";
import { Search, Heart, Bell, User, LogOut, Menu, X, Car } from "lucide-react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

interface NavbarProps {
  onSearchToggle?: () => void;
}

export default function Navbar({ onSearchToggle }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [user, setUser] = useState<{ id: number; email: string } | null>(null);
  const router = useRouter();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (isRegister) {
        await api.register(email, password);
      }
      const { access_token } = await api.login(email, password);
      localStorage.setItem("token", access_token);
      const me = await api.getMe();
      setUser(me);
      setAuthOpen(false);
      setEmail("");
      setPassword("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error de autenticacion";
      if (message.includes("401") || message.includes("Credenciales")) {
        setError("Email o contrasena incorrectos");
      } else if (message.includes("400") || message.includes("registrado")) {
        setError("Este email ya esta registrado");
      } else {
        setError(message || "Error al conectar con el servidor");
      }
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setAuthOpen(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <><nav className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--background)]/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <a href="/" className="flex items-center gap-2 text-xl font-bold">
          <Car className="h-6 w-6 text-[var(--primary)]" />
          <span>Autoradar</span>
        </a>

        <div className="hidden items-center gap-6 md:flex">
          <button
            onClick={onSearchToggle}
            className="flex items-center gap-2 text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
          >
            <Search className="h-4 w-4" />
            Buscar
          </button>
          <a
            href="/favoritos"
            className="flex items-center gap-2 text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
          >
            <Heart className="h-4 w-4" />
            Favoritos
          </a>
          {user && (
            <a
              href="/alertas"
              className="flex items-center gap-2 text-sm text-[var(--muted)] transition-colors hover:text-[var(--foreground)]"
            >
              <Bell className="h-4 w-4" />
              Alertas
            </a>
          )}
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-[var(--muted)]">{user.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-lg bg-[var(--secondary)] px-3 py-2 text-sm transition-colors hover:bg-[var(--border)]"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setAuthOpen(true)}
              className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
            >
              <User className="h-4 w-4" />
              Ingresar
            </button>
          )}
        </div>

        <button
          className="md:hidden"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-[var(--border)] px-4 py-4 md:hidden">
          <div className="flex flex-col gap-3">
            <button
              onClick={() => {
                onSearchToggle?.();
                setMenuOpen(false);
              }}
              className="flex items-center gap-2 text-sm"
            >
              <Search className="h-4 w-4" /> Buscar
            </button>
            <a href="/favoritos" className="flex items-center gap-2 text-sm">
              <Heart className="h-4 w-4" /> Favoritos
            </a>
            {user && (
              <a href="/alertas" className="flex items-center gap-2 text-sm">
                <Bell className="h-4 w-4" /> Alertas
              </a>
            )}
            {user ? (
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 text-sm text-red-400"
              >
                <LogOut className="h-4 w-4" /> Cerrar sesion
              </button>
            ) : (
              <button
                onClick={() => {
                  setAuthOpen(true);
                  setMenuOpen(false);
                }}
                className="flex items-center gap-2 text-sm"
              >
                <User className="h-4 w-4" /> Ingresar
              </button>
            )}
          </div>
        </div>
      )}

    </nav>
      {authOpen && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto bg-black/70 py-8"
          onClick={handleOverlayClick}
        >
          <div className="w-full max-w-sm rounded-xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-2xl">
            <div className="mb-6 text-center">
              <h2 className="text-xl font-bold">
                {isRegister ? "Crear cuenta" : "Iniciar sesion"}
              </h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                {isRegister
                  ? "Registrate para guardar favoritos y alertas"
                  : "Ingresa con tu email y contrasena"}
              </p>
            </div>
            <form onSubmit={handleAuth} className="flex flex-col gap-4">
              <div>
                <label className="mb-1.5 block text-xs font-medium text-[var(--muted)]">
                  Email
                </label>
                <input
                  type="email"
                  placeholder="ej: usuario@correo.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-4 py-2.5 text-sm outline-none transition-colors placeholder:text-[var(--muted)] focus:border-[var(--primary)]"
                  required
                  autoFocus
                />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium text-[var(--muted)]">
                  Contrasena
                </label>
                <input
                  type="password"
                  placeholder="Ingresa tu contrasena"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--secondary)] px-4 py-2.5 text-sm outline-none transition-colors placeholder:text-[var(--muted)] focus:border-[var(--primary)]"
                  required
                />
              </div>
              {error && (
                <div className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400">
                  {error}
                </div>
              )}
              <button
                type="submit"
                className="rounded-lg bg-[var(--primary)] py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--primary-hover)] active:scale-[0.98]"
              >
                {isRegister ? "Registrarse" : "Ingresar"}
              </button>
            </form>
            <div className="mt-5 flex flex-col items-center gap-2">
              <button
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError("");
                }}
                className="text-sm text-[var(--primary)] transition-colors hover:text-[var(--primary-hover)] hover:underline"
              >
                {isRegister ? "Ya tengo una cuenta" : "Crear cuenta nueva"}
              </button>
              <button
                onClick={() => setAuthOpen(false)}
                className="mt-1 w-full rounded-lg border border-[var(--border)] py-2 text-sm text-[var(--muted)] transition-colors hover:bg-[var(--secondary)] hover:text-[var(--foreground)]"
              >
                Cancelar
              </button>
            </div>
            <p className="mt-5 text-center text-xs text-[var(--muted)]">
              Demo: demo@autoradar.co / demo123
            </p>
          </div>
        </div>
      )}
    </>
  );
}
