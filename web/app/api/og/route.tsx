import { ImageResponse } from "next/og";

export const runtime = "edge";
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const COLOR: Record<string, string> = { HONEST: "#16a34a", "MOSTLY HONEST": "#65a30d", SNEAKY: "#ea580c", LIAR: "#dc2626" };

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const id = searchParams.get("id");
  let verdict = "RECEIPT", grade = "?", repo = "RoboTruth", title = "Did the robot lie?";
  if (id) {
    try {
      const r = await fetch(`${BASE}/api/receipt/${id}`);
      if (r.ok) { const d = await r.json(); verdict = d.verdict; grade = d.grade; repo = `${d.pr.repo} #${d.pr.number}`; title = d.pr.title; }
    } catch {
      // receipt fetch failed — use defaults
    }
  }
  const c = COLOR[verdict] ?? "#111827";
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: 64, background: "#ffffff", fontFamily: "sans-serif" }}>
        <div style={{ fontSize: 28, color: "#6b7280" }}>RoboTruth · INTENT RECEIPT</div>
        <div style={{ fontSize: 34, color: "#111827", marginTop: 8 }}>{repo}</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 24, marginTop: 24 }}>
          <div style={{ fontSize: 96, fontWeight: 800, color: c }}>{verdict}</div>
          <div style={{ fontSize: 72, fontWeight: 800, color: c }}>{grade}</div>
        </div>
        <div style={{ fontSize: 30, color: "#374151", marginTop: 24 }}>{title}</div>
        <div style={{ fontSize: 24, color: "#9ca3af", marginTop: 40 }}>Did the robot lie? — paste any PR.</div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
