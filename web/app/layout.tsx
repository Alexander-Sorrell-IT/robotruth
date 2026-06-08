import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import Script from "next/script";
import { PendoInitializer } from "@/components/PendoInitializer";
import "./globals.css";
import styles from "./layout.module.css";

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
      <head>
        <Script id="pendo-install" strategy="afterInteractive">{`
(function(apiKey){
    (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
    v=['initialize','identify','updateOptions','pageLoad','track','trackAgent'];for(w=0,x=v.length;w<x;++w)(function(m){
    o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
    y=e.createElement(n);y.async=!0;y.src='https://cdn.pendo.io/agent/static/'+apiKey+'/pendo.js';
    z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(window,document,'script','pendo');
})('1ff203ba-d6b6-456d-a4c1-5d0b84aab3f8');
        `}</Script>
      </head>
      <body>
        <PendoInitializer />
        <header className={styles.header}>
          <Link href="/" className={styles.wordmark}>
            <svg
              className={styles.glyph}
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M5 3.5v17l2-1.2 2 1.2 2-1.2 2 1.2 2-1.2 2 1.2v-17l-2 1.2-2-1.2-2 1.2-2-1.2-2 1.2-2-1.2z" />
              <path d="M8.5 11.5l2.2 2.2 4.3-4.3" />
            </svg>
            RoboTruth
          </Link>
          <nav className={styles.nav}>
            <Link href="/wall" className={styles.navLink}>Wall of Shame</Link>
            <Link href="/bots" className={styles.navLink}>Bot Leaderboard</Link>
            <Link href="/insights" className={styles.navLink}>Insights</Link>
            <Link href="/badge" className={styles.navLink}>Badge</Link>
          </nav>
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
