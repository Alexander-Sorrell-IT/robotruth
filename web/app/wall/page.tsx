import { TrackView } from "@/components/TrackView";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const COLOR: Record<string, string> = { SNEAKY: "#ea580c", LIAR: "#dc2626" };

interface WallItem {
  id: string;
  repo: string;
  number: number;
  title: string;
  verdict: string;
  grade: string;
  author: string | null;
}

async function getWall(): Promise<WallItem[]> {
  try {
    const r = await fetch(`${BASE}/api/wall`, { cache: "no-store" });
    if (!r.ok) return [];
    return (await r.json()).items as WallItem[];
  } catch {
    return [];
  }
}

export const metadata = { title: "Wall of Shame — RoboTruth" };

export default async function WallPage() {
  const items = await getWall();
  return (
    <main
      style={{
        maxWidth: 720,
        margin: "0 auto",
        padding: "48px 16px",
      }}
    >
      <TrackView event="wall_view" />
      <div
        style={{
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: "#6b7280",
          marginBottom: 10,
        }}
      >
        The Receipts Protocol · audit feed
      </div>
      <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em", margin: 0 }}>
        Wall of Shame
      </h1>
      <p style={{ color: "#4b5563", marginTop: 10, fontSize: 16, lineHeight: 1.55 }}>
        Public bot-authored PRs that claimed one thing and quietly did another. Every receipt
        below is a real catch — verdict, grade, file:line evidence, no AI guessing.
      </p>

      {items.length === 0 ? (
        <div
          style={{
            marginTop: 32,
            padding: "24px 22px",
            borderRadius: 14,
            background: "#f0fdf4",
            border: "1px solid #bbf7d0",
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "#15803d",
              marginBottom: 6,
            }}
          >
            ● Live · scanning
          </div>
          <div style={{ fontSize: 17, fontWeight: 700, color: "#14532d", lineHeight: 1.3 }}>
            No sneaky PRs caught right now. The bots are behaving.
          </div>
          <p style={{ marginTop: 10, fontSize: 14, color: "#166534", lineHeight: 1.55 }}>
            Every public PR audited through RoboTruth flows through this feed. Only{" "}
            <strong>SNEAKY</strong> or <strong>LIAR</strong> verdicts get pinned here —
            human authors anonymized, bots named. When the next catch lands, it shows up below.
          </p>
          <div style={{ marginTop: 16, display: "flex", gap: 8, flexWrap: "wrap" }}>
            <a
              href="/"
              style={{
                padding: "9px 16px",
                borderRadius: 8,
                background: "#111827",
                color: "#fff",
                fontSize: 14,
                fontWeight: 500,
                textDecoration: "none",
              }}
            >
              Audit a PR →
            </a>
            <a
              href="/repo/facebook/react"
              style={{
                padding: "9px 16px",
                borderRadius: 8,
                background: "#fff",
                border: "1px solid #bbf7d0",
                color: "#166534",
                fontSize: 14,
                fontWeight: 500,
                textDecoration: "none",
              }}
            >
              Score a whole repo →
            </a>
          </div>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, marginTop: 28 }}>
          {items.map((it) => (
            <li
              key={it.id}
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                padding: 16,
                marginBottom: 12,
                background: "#fff",
              }}
            >
              <a href={`/r/${it.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                  <span
                    style={{
                      fontWeight: 800,
                      color: COLOR[it.verdict] ?? "#dc2626",
                      fontSize: 14,
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {it.verdict} · {it.grade}
                  </span>
                  <span style={{ color: "#6b7280", fontSize: 13 }}>
                    {it.repo} #{it.number}
                    {it.author ? ` · ${it.author}` : ""}
                  </span>
                </div>
                <div style={{ marginTop: 6, fontSize: 15, color: "#111827", lineHeight: 1.4 }}>
                  {it.title}
                </div>
              </a>
            </li>
          ))}
        </ul>
      )}

      <p
        style={{
          marginTop: 36,
          fontSize: 11,
          color: "#9ca3af",
          textAlign: "center",
          lineHeight: 1.55,
        }}
      >
        Wall attribution policy: bots named (dependabot, copilot, cursor-bot, etc.) · human
        authors anonymized · opt-in for human-authored receipts.
      </p>
    </main>
  );
}
