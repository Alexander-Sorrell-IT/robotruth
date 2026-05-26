import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
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
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  title: "RoboTruth — Did the robot lie?",
  description: "The Receipts Protocol — a deterministic record of what AI agents claimed vs what they actually did. First surface: GitHub PRs. No model in the verdict path.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <header style={{
          position: "sticky",
          top: 0,
          zIndex: 50,
          background: "rgba(250,250,250,0.92)",
          backdropFilter: "blur(8px)",
          borderBottom: "1px solid #e5e7eb",
          padding: "0 24px",
          height: 52,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <Link href="/" style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-0.01em" }}>
            🤖 RoboTruth
          </Link>
          <Link href="/wall" style={{ fontSize: 14, color: "#6b7280" }}>
            Wall of Shame
          </Link>
        </header>

        <div style={{ flex: 1 }}>
          {children}
        </div>

        <footer style={{
          borderTop: "1px solid #e5e7eb",
          padding: "16px 24px",
          textAlign: "center",
          fontSize: 12,
          color: "#9ca3af",
        }}>
          The Receipts Protocol · deterministic verdicts · no model in the verdict path
        </footer>
      </body>
    </html>
  );
}
