import { ImageResponse } from "next/og";

export const runtime = "edge";
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const COLOR: Record<string, string> = {
  HONEST: "#16a34a",
  "MOSTLY HONEST": "#65a30d",
  SNEAKY: "#ea580c",
  LIAR: "#dc2626",
};
const BG: Record<string, string> = {
  HONEST: "#f0fdf4",
  "MOSTLY HONEST": "#f7fee7",
  SNEAKY: "#fff7ed",
  LIAR: "#fef2f2",
};

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const id = searchParams.get("id");
  let verdict = "RECEIPT";
  let grade = "?";
  let repo = "RoboTruth";
  let title = "Did the robot lie?";
  let und = 0;
  let unh = 0;
  let del = 0;
  if (id) {
    try {
      const r = await fetch(`${BASE}/api/receipt/${id}`);
      if (r.ok) {
        const d = await r.json();
        verdict = String(d.verdict ?? "RECEIPT");
        grade = String(d.grade ?? "?");
        repo = d.pr ? `${d.pr.repo} #${d.pr.number}` : "RoboTruth";
        title = String(d.pr?.title ?? "Did the robot lie?");
        und = d.undisclosed?.length ?? 0;
        unh = d.unhonored?.length ?? 0;
        del = d.delivered?.length ?? 0;
      }
    } catch {
      // receipt fetch failed — use defaults
    }
  }
  const c = COLOR[verdict] ?? "#111827";
  const bg = BG[verdict] ?? "#ffffff";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          padding: 56,
          background: bg,
          fontFamily: "sans-serif",
        }}
      >
        {/* Top stripe — brand + category */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: 22,
            color: "#6b7280",
            letterSpacing: 1,
          }}
        >
          <div>ROBOTRUTH · INTENT RECEIPT</div>
          <div style={{ fontWeight: 700 }}>THE RECEIPTS PROTOCOL</div>
        </div>

        {/* Repo + PR */}
        <div style={{ fontSize: 32, color: "#111827", marginTop: 28 }}>{repo}</div>

        {/* Verdict slam */}
        <div style={{ display: "flex", alignItems: "baseline", gap: 28, marginTop: 18 }}>
          <div
            style={{
              fontSize: 108,
              fontWeight: 900,
              color: c,
              letterSpacing: -2,
              lineHeight: 1,
            }}
          >
            {verdict}
          </div>
          <div
            style={{
              fontSize: 84,
              fontWeight: 900,
              color: c,
              border: `4px solid ${c}`,
              borderRadius: 18,
              padding: "0 26px",
              lineHeight: 1.1,
            }}
          >
            {grade}
          </div>
        </div>

        {/* PR title */}
        <div
          style={{
            fontSize: 32,
            color: "#1f2937",
            marginTop: 22,
            lineHeight: 1.3,
            overflow: "hidden",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
          }}
        >
          {title}
        </div>

        {/* Flag breakdown — the story the verdict tells */}
        <div style={{ display: "flex", gap: 28, marginTop: 26, fontSize: 24 }}>
          <div style={{ color: und > 0 ? "#ea580c" : "#9ca3af" }}>
            <span style={{ fontWeight: 700, fontSize: 30 }}>{und}</span> undisclosed
          </div>
          <div style={{ color: unh > 0 ? "#dc2626" : "#9ca3af" }}>
            <span style={{ fontWeight: 700, fontSize: 30 }}>{unh}</span> unhonored
          </div>
          <div style={{ color: del > 0 ? "#16a34a" : "#9ca3af" }}>
            <span style={{ fontWeight: 700, fontSize: 30 }}>{del}</span> delivered
          </div>
        </div>

        {/* Footer constraint — the brand */}
        <div
          style={{
            marginTop: "auto",
            fontSize: 22,
            color: "#4b5563",
            paddingTop: 24,
            borderTop: "1px solid #e5e7eb",
          }}
        >
          Deterministic · every flag cites file:line · <span style={{ fontWeight: 700, color: "#111827" }}>no model in the verdict path.</span>
        </div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
