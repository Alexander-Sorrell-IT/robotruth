import type { Receipt, Flag } from "@/lib/receipt";

const VERDICT_COLOR: Record<string, string> = {
  HONEST: "#16a34a", "MOSTLY HONEST": "#65a30d", SNEAKY: "#ea580c", LIAR: "#dc2626",
};

function Bucket({ title, icon, flags }: { title: string; icon: string; flags: Flag[] }) {
  if (flags.length === 0) return null;
  return (
    <div style={{ marginTop: 16 }}>
      <h3 style={{ margin: 0, fontSize: 14, textTransform: "uppercase", letterSpacing: 1 }}>{icon} {title}</h3>
      <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
        {flags.map((f, i) => (
          <li key={i} style={{ marginBottom: 4 }}>
            {f.label}{f.file ? ` — ${f.file}${f.line ? `:${f.line}` : ""}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ReceiptCard({ receipt }: { receipt: Receipt }) {
  const c = VERDICT_COLOR[receipt.verdict] ?? "#444";
  return (
    <div style={{ maxWidth: 640, margin: "0 auto", border: "1px solid #e5e7eb", borderRadius: 12, padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <div style={{ fontSize: 12, color: "#6b7280" }}>INTENT RECEIPT · {receipt.pr.repo} #{receipt.pr.number}</div>
      <div style={{ fontSize: 16, fontWeight: 600, marginTop: 4 }}>{receipt.pr.title}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 16 }}>
        <span style={{ fontSize: 34, fontWeight: 800, color: c }}>{receipt.verdict}</span>
        <span style={{ fontSize: 22, fontWeight: 700, color: c }}>{receipt.grade}</span>
      </div>
      <Bucket title="Did, but didn&apos;t mention" icon="⚠️" flags={receipt.undisclosed} />
      <Bucket title="Claimed, but not found" icon="❌" flags={receipt.unhonored} />
      <Bucket title="Claimed &amp; delivered" icon="✅" flags={receipt.delivered} />
      {receipt.parsed_claims.length > 0 && (
        <div style={{ marginTop: 16, fontSize: 12, color: "#6b7280" }}>
          We read this PR as promising: {receipt.parsed_claims.join("; ")}
        </div>
      )}
      <div style={{ marginTop: 12, fontSize: 11, color: "#9ca3af" }}>
        Deterministic. Every flag cites file:line. No AI opinions. — {receipt.math}
      </div>
    </div>
  );
}
