import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Autoradar - Comparador Inteligente de Vehículos",
  description: "Encuentra las mejores oportunidades en vehículos usados en Colombia. Compara precios, historial y recibe alertas.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
