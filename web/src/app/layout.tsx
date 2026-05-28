import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Reci — Reciclaje inteligente en la PUCE",
    template: "%s · Reci",
  },
  description:
    "Robot autónomo de reciclaje para el campus PUCE Sede Manabí. Clasifica vidrio y plástico, te llama al punto más cercano y te recompensa por reciclar.",
  applicationName: "Reci",
  keywords: ["reciclaje", "PUCE", "Manabí", "IoT", "sistema experto", "robot"],
  authors: [{ name: "Equipo Reci — PUCE Manabí" }],
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  themeColor: "#0f9d58",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
        {children}
      </body>
    </html>
  );
}
