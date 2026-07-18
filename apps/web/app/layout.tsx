import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://vibemaxxing.dev"),
  title: "vibemaxxing — the competitive ledger",
  description: "Public competition. Private transcripts. Compare AI-agent activity without exposing your work.",
  icons: { icon: "/brand/favicon.svg" },
  openGraph: {
    title: "vibemaxxing — the competitive ledger",
    description: "Burn more. Rank higher.",
    images: ["/brand/social-card.svg"],
  },
};

export const viewport: Viewport = {
  themeColor: "#f4f2ed",
  colorScheme: "light",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
