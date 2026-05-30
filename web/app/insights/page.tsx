const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

interface Stats {
  total_receipts: number;
  wall_count: number;
  verdict_distribution: {
    HONEST?: number;
    "MOSTLY HONEST"?: number;
    SNEAKY?: number;
    LIAR?: number;
  };
  scanners_fired: {
    dangerous_primitives?: number;
    dependencies?: number;
    scope_drift?: number;
    security_guard?: number;
  };
  flags_total: number;
}

async function getStats(): Promise<Stats | null> {
  try {
    const r = await fetch(`${BASE}/api/stats`, { cache: "no-store" });
    if (!r.ok) return null;
    return (await r.json()) as Stats;
  } catch {
    return null;
  }
}

const VERDICT_STYLE: Record<
  string,
  { bg: string; text: string; border: string; label: string }
> = {
  HONEST: { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0", label: "HONEST" },
  "MOSTLY HONEST": { bg: "#f7fee7", text: "#4d7c0f", border: "#d9f99d", label: "MOSTLY HONEST" },
  SNEAKY: { bg: "#fffbeb", text: "#d97706", border: "#fde68a", label: "SNEAKY" },
  LIAR: { bg: "#fef2f2", text: "#dc2626", border: "#fecaca", label: "LIAR" },
};

const SCANNER_LABELS: Record<string, string> = {
  dangerous_primitives: "Dangerous Primitives",
  dependencies: "Dependencies",
  scope_drift: "Scope Drift",
  security_guard: "Security Guard",
};

export const metadata = { title: "Live Insights — RoboTruth" };

export default async function InsightsPage() {
  const stats = await getStats();

  const empty = !stats || stats.total_receipts === 0;

  return (
    <main
      style={{
        maxWidth: 680,
        margin: "0 auto",
        padding: "48px 24px 80px",
        fontFamily: "ui-sans-serif, system-ui",
      }}
    >
      {/* Header */}
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
        Receipts Protocol · Live Insights
      </div>
      <h1
        style={{
          fontSize: 32,
          fontWeight: 800,
          letterSpacing: "-0.02em",
          margin: 0,
          color: "#111827",
        }}
      >
        What the robots are doing
      </h1>
      <p style={{ color: "#4b5563", marginTop: 10, fontSize: 16, lineHeight: 1.55 }}>
        Real-time stats from every receipt generated through RoboTruth. Deterministic —
        no model in the verdict path.
      </p>

      {empty ? (
        /* Empty state */
        <div
          style={{
            marginTop: 40,
            padding: "32px 28px",
            borderRadius: 14,
            background: "#f9fafb",
            border: "1px solid #e5e7eb",
            textAlign: "center",
          }}
        >
          <div
            style={{ fontSize: 40, marginBottom: 16 }}
            aria-hidden="true"
          >
            📭
          </div>
          <div
            style={{ fontSize: 20, fontWeight: 700, color: "#111827", marginBottom: 8 }}
          >
            No receipts generated yet — be the first!
          </div>
          <p style={{ color: "#6b7280", fontSize: 15, lineHeight: 1.55, margin: 0 }}>
            Audit a public GitHub PR and the stats will appear here instantly.
          </p>
          <a
            href="/"
            style={{
              display: "inline-block",
              marginTop: 20,
              padding: "11px 22px",
              borderRadius: 10,
              background: "#111827",
              color: "#fff",
              fontSize: 15,
              fontWeight: 600,
              textDecoration: "none",
            }}
          >
            Audit a PR →
          </a>
        </div>
      ) : (
        <>
          {/* Big stat */}
          <div
            style={{
              marginTop: 40,
              padding: "28px 28px",
              borderRadius: 14,
              background: "#111827",
              color: "#fff",
            }}
          >
            <div
              style={{
                fontSize: 56,
                fontWeight: 800,
                letterSpacing: "-0.03em",
                lineHeight: 1,
              }}
            >
              {stats!.total_receipts.toLocaleString()}
            </div>
            <div
              style={{ fontSize: 17, fontWeight: 500, marginTop: 8, color: "#d1d5db" }}
            >
              receipts generated
            </div>
            <div style={{ fontSize: 14, marginTop: 10, color: "#9ca3af" }}>
              {stats!.wall_count.toLocaleString()} caught on the Wall of Shame
            </div>
          </div>

          {/* Verdict distribution */}
          <div style={{ marginTop: 32 }}>
            <div
              style={{
                fontSize: 13,
                fontWeight: 700,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
                color: "#6b7280",
                marginBottom: 14,
              }}
            >
              Verdict distribution
            </div>
            <div
              style={{
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
              }}
            >
              {(["HONEST", "MOSTLY HONEST", "SNEAKY", "LIAR"] as const).map((v) => {
                const count = stats!.verdict_distribution[v] ?? 0;
                const style = VERDICT_STYLE[v];
                return (
                  <div
                    key={v}
                    style={{
                      padding: "12px 18px",
                      borderRadius: 10,
                      background: style.bg,
                      border: `1px solid ${style.border}`,
                      minWidth: 100,
                      flex: "1 1 auto",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 24,
                        fontWeight: 800,
                        color: style.text,
                        letterSpacing: "-0.02em",
                      }}
                    >
                      {count.toLocaleString()}
                    </div>
                    <div
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        color: style.text,
                        letterSpacing: "0.06em",
                        marginTop: 4,
                        opacity: 0.85,
                      }}
                    >
                      {style.label}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Flags by scanner */}
          <div style={{ marginTop: 32 }}>
            <div
              style={{
                fontSize: 13,
                fontWeight: 700,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
                color: "#6b7280",
                marginBottom: 14,
              }}
            >
              Flags by scanner
            </div>
            <div
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                overflow: "hidden",
                background: "#fff",
              }}
            >
              {(() => {
                const scanners = stats!.scanners_fired;
                const entries = Object.entries(SCANNER_LABELS)
                  .map(([key, label]) => ({
                    key,
                    label,
                    count: (scanners as Record<string, number | undefined>)[key] ?? 0,
                  }))
                  .sort((a, b) => b.count - a.count);

                const max = Math.max(...entries.map((e) => e.count), 1);

                return entries.map((entry, i) => (
                  <div
                    key={entry.key}
                    style={{
                      padding: "14px 18px",
                      borderTop: i === 0 ? "none" : "1px solid #f3f4f6",
                      display: "flex",
                      alignItems: "center",
                      gap: 14,
                    }}
                  >
                    <div style={{ width: 150, fontSize: 14, color: "#374151", fontWeight: 500, flexShrink: 0 }}>
                      {entry.label}
                    </div>
                    <div style={{ flex: 1, background: "#f3f4f6", borderRadius: 4, height: 8, overflow: "hidden" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${(entry.count / max) * 100}%`,
                          background: entry.count > 0 ? "#f59e0b" : "transparent",
                          borderRadius: 4,
                          transition: "width 0.3s ease",
                        }}
                      />
                    </div>
                    <div
                      style={{
                        fontSize: 14,
                        fontWeight: 700,
                        color: entry.count > 0 ? "#111827" : "#d1d5db",
                        minWidth: 28,
                        textAlign: "right",
                      }}
                    >
                      {entry.count.toLocaleString()}
                    </div>
                  </div>
                ));
              })()}
            </div>
            <div style={{ marginTop: 8, fontSize: 13, color: "#9ca3af" }}>
              Total flags raised: <strong style={{ color: "#374151" }}>{stats!.flags_total.toLocaleString()}</strong>
            </div>
          </div>

          {/* Footer note */}
          <p
            style={{
              marginTop: 40,
              fontSize: 12,
              color: "#9ca3af",
              lineHeight: 1.6,
              borderTop: "1px solid #f3f4f6",
              paddingTop: 20,
            }}
          >
            Data from receipts stored in this session. Novus integration pending for full
            funnel analytics.
          </p>
        </>
      )}
    </main>
  );
}
