const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const COLOR: Record<string, string> = { SNEAKY: "#ea580c", LIAR: "#dc2626" };

interface WallItem { id: string; repo: string; number: number; title: string; verdict: string; grade: string; author: string | null; }

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
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px", fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 30, fontWeight: 800 }}>Wall of Shame</h1>
      <p style={{ color: "#6b7280" }}>The sneakiest AI-written PRs we&apos;ve caught — claimed one thing, did another.</p>
      {items.length === 0 ? (
        <p style={{ marginTop: 24, color: "#9ca3af" }}>Nothing caught yet. <a href="/">Audit a PR →</a></p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, marginTop: 24 }}>
          {items.map((it) => (
            <li key={it.id} style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 16, marginBottom: 12 }}>
              <a href={`/r/${it.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <span style={{ fontWeight: 800, color: COLOR[it.verdict] ?? "#dc2626" }}>{it.verdict} · {it.grade}</span>
                <span style={{ color: "#6b7280" }}> — {it.repo} #{it.number}{it.author ? ` · ${it.author}` : ""}</span>
                <div style={{ marginTop: 4 }}>{it.title}</div>
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
