import type { Metadata, Viewport } from "next";
import "@vibemaxxing/ui/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://vibemaxxing.dev"),
  title: "vibemaxxing — the competitive ledger",
  description: "Public competition. Private transcripts. Compare AI-agent activity without exposing your work.",
  // D-637 deleted the brand and the governed asset library, including the public
  // brand directory this block pointed an icon and a social card at. The entries
  // are removed rather than repointed: no replacement mark exists and no path is
  // reserved for one.
  openGraph: {
    title: "vibemaxxing — the competitive ledger",
    description: "Burn more. Rank higher.",
  },
};

// themeColor came from the deleted brand palette and is removed with it. colorScheme
// is a rendering hint rather than a brand value, so it stays.
export const viewport: Viewport = {
  colorScheme: "light",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
