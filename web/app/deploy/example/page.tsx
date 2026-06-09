import Link from "next/link";

export const metadata = {
  title: "Deploy Receipt — RoboTruth",
  description:
    "The Receipts Protocol grammar applied to a deployment-agent claim — computed by the same deterministic engine as the PR receipt. Same verdict words, same three buckets, same resource:line citations. No model in the verdict path.",
};

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

// Render this on every request so the receipt is genuinely computed by the engine,
// not baked at build time.
export const dynamic = "force-dynamic";

interface Flag {
  label: string;
  file: string;
  line: number | null;
  severity: "critical" | "moderate" | "minor";
  evidence: string;
}
interface DeployReceipt {
  deploy: { service: string; release: string; title: string; claim: string };
  verdict: "HONEST" | "MOSTLY HONEST" | "SNEAKY" | "LIAR";
  grade: string;
  delivered: Flag[];
  undisclosed: Flag[];
  unhonored: Flag[];
  scanners: string[];
  math: string;
}

const VERDICT_COLOR: Record<string, string> = {
  HONEST: "#16a34a",
  "MOSTLY HONEST": "#65a30d",
  SNEAKY: "#ea580c",
  LIAR: "#dc2626",
};
const VERDICT_BG: Record<string, string> = {
  HONEST: "#f0fdf4",
  "MOSTLY HONEST": "#f7fee7",
  SNEAKY: "#fff7ed",
  LIAR: "#fef2f2",
};

async function getDeployExample(): Promise<DeployReceipt | null> {
  try {
    const r = await fetch(`${BASE}/api/deploy/example`, { cache: "no-store" });
    if (!r.ok) return null;
    return (await r.json()) as DeployReceipt;
  } catch {
    return null;
  }
}

function Bucket({
  title,
  icon,
  color,
  flags,
}: {
  title: string;
  icon: string;
  color: string;
  flags: Flag[];
}) {
  if (flags.length === 0) return null;
  return (
    <div style={{ marginTop: 16, borderLeft: `3px solid ${color}`, paddingLeft: 12 }}>
      <h3
        style={{
          margin: 0,
          fontSize: 11,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.07em",
          color,
        }}
      >
        {icon} {title}
      </h3>
      <ul style={{ margin: "8px 0 0", paddingLeft: 0, listStyle: "none" }}>
        {flags.map((f, i) => (
          <li
            key={i}
            style={{
              padding: "8px 0",
              borderBottom: i < flags.length - 1 ? "1px solid #f3f4f6" : "none",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "baseline" }}>
              <span style={{ fontSize: 13, color: "#111827", flex: 1 }}>{f.label}</span>
              <span
                style={{
                  fontFamily: "var(--mono)",
                  fontSize: 11,
                  color: "#9ca3af",
                  whiteSpace: "nowrap",
                  flexShrink: 0,
                }}
              >
                {f.file}
                {f.line != null ? `:${f.line}` : ""}
              </span>
            </div>
            {f.evidence ? (
              <pre
                style={{
                  margin: "6px 0 0",
                  padding: "8px 10px",
                  background: "#f9fafb",
                  fontSize: 11,
                  color: "#374151",
                  borderRadius: 6,
                  fontFamily: "var(--mono)",
                  whiteSpace: "pre-wrap",
                  overflow: "hidden",
                }}
              >
                {f.evidence}
              </pre>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default async function DeployExamplePage() {
  const receipt = await getDeployExample();

  if (!receipt) {
    return (
      <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px" }}>
        <h1 style={{ fontSize: 24, fontWeight: 800 }}>Deploy Receipt</h1>
        <p style={{ color: "#6b7280", marginTop: 12 }}>
          Live computation is temporarily unavailable. The Deploy Receipt is computed by the
          RoboTruth engine — try again in a moment.
        </p>
        <Link href="/" style={{ color: "#2563eb" }}>← Back to the PR receipt</Link>
      </main>
    );
  }

  const color = VERDICT_COLOR[receipt.verdict] ?? "#ea580c";
  const bg = VERDICT_BG[receipt.verdict] ?? "#fff7ed";
  const flagCount = receipt.undisclosed.length + receipt.unhonored.length;

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px" }}>
      {/* Honest note: this is a real computation of an example deployment */}
      <div
        style={{
          marginBottom: 24,
          padding: "12px 16px",
          background: "#f0f9ff",
          border: "1px solid #bae6fd",
          borderRadius: 10,
          fontSize: 13,
          color: "#075985",
          lineHeight: 1.5,
        }}
      >
        <strong>The second surface — computed, not authored.</strong> This receipt is produced
        by the RoboTruth engine from an example deployment manifest diff, using the{" "}
        <em>same pure grader</em> as the{" "}
        <Link href="/" style={{ color: "#0369a1", textDecoration: "underline" }}>
          PR receipt
        </Link>
        . Different scanners, identical grammar. No model in the verdict path.
      </div>

      {/* Category header */}
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
        The Receipts Protocol · surface: deployment agent
      </div>
      <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em", margin: 0 }}>
        Deploy Receipt
      </h1>
      <p style={{ color: "#4b5563", marginTop: 10, fontSize: 15, lineHeight: 1.55 }}>
        Compares what the deployment agent <em>claimed</em> in its release note against what
        the diff between previous and current cluster state <em>actually</em> shows.
      </p>

      {/* The card itself */}
      <div
        style={{
          marginTop: 28,
          background: "#ffffff",
          border: "1px solid #e5e7eb",
          borderRadius: 16,
          boxShadow: "0 4px 24px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04)",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div style={{ padding: "16px 24px", borderBottom: "1px solid #f3f4f6" }}>
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "#9ca3af",
            }}
          >
            RoboTruth · DEPLOY RECEIPT &nbsp;·&nbsp; {receipt.deploy.service} · release{" "}
            {receipt.deploy.release}
          </div>
          <div
            style={{
              fontSize: 17,
              fontWeight: 700,
              marginTop: 6,
              color: "#111827",
              lineHeight: 1.35,
            }}
          >
            {receipt.deploy.title}
          </div>
        </div>

        {/* Verdict block */}
        <div
          style={{
            padding: "20px 24px",
            background: bg,
            borderBottom: "1px solid #f3f4f6",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              padding: "6px 16px",
              borderRadius: 999,
              background: `${color}18`,
              color,
              fontSize: 20,
              fontWeight: 800,
              letterSpacing: "-0.01em",
            }}
          >
            {receipt.verdict}
          </span>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: 48,
              height: 48,
              borderRadius: 10,
              background: `${color}18`,
              color,
              fontSize: 28,
              fontWeight: 800,
            }}
          >
            {receipt.grade}
          </span>
        </div>

        {/* Audit summary */}
        <div
          style={{
            padding: "14px 24px",
            background: "#fafafa",
            borderBottom: "1px solid #f3f4f6",
            fontSize: 12.5,
            color: "#374151",
            lineHeight: 1.55,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: 10.5,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "#6b7280",
              marginBottom: 6,
            }}
          >
            <span style={{ color }}>●</span> Audit ran · {receipt.scanners.length} scanners ·{" "}
            {flagCount} flag{flagCount === 1 ? "" : "s"} raised
          </div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "#9ca3af" }}>
            {receipt.scanners.join(" · ")}
          </div>
        </div>

        {/* Buckets */}
        <div style={{ padding: "8px 24px 4px" }}>
          <Bucket title="Did, but didn't mention" icon="⚠️" color="#ea580c" flags={receipt.undisclosed} />
          <Bucket title="Claimed, but contradicted by deploy" icon="❌" color="#dc2626" flags={receipt.unhonored} />
          <Bucket title="Claimed & delivered" icon="✅" color="#16a34a" flags={receipt.delivered} />
        </div>

        {/* Footer */}
        <div style={{ padding: "16px 24px", borderTop: "1px solid #f3f4f6", marginTop: 8 }}>
          <div style={{ fontSize: 11, color: "#9ca3af", marginBottom: 0 }}>
            Deterministic · every flag cites resource:line · no model in the verdict path &nbsp;·&nbsp;
            {receipt.math}
          </div>
        </div>
      </div>

      {/* The thesis */}
      <div
        style={{
          marginTop: 36,
          padding: "20px 22px",
          background: "#f9fafb",
          border: "1px solid #e5e7eb",
          borderRadius: 12,
        }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "#6b7280",
            marginBottom: 8,
          }}
        >
          Why this matters
        </div>
        <p style={{ margin: 0, fontSize: 14, color: "#374151", lineHeight: 1.65 }}>
          A deploy receipt is the same primitive as a PR receipt: read the agent&apos;s claim, read
          the actual change, cite every divergence. The scanners are different (manifest drift,
          probe changes, rollout target, env var surface — instead of dangerous primitives,
          dependencies, scope drift, security guard) but the grader is <em>the same pure
          function</em>. One verdict word. One letter grade. Three buckets. Evidence at{" "}
          <code>resource:line</code>. No model in the verdict path.
        </p>
        <p style={{ margin: "12px 0 0", fontSize: 14, color: "#374151", lineHeight: 1.65 }}>
          PRs were the first surface because the diff is the ground truth and it&apos;s public.
          Deployments are next because the cost of being lied to is the highest — the agent
          claimed staging, it shipped production, the incident already happened.
        </p>
      </div>

      {/* Nav */}
      <div style={{ marginTop: 32, display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Link
          href="/"
          style={{
            padding: "10px 18px",
            background: "#111827",
            color: "#fff",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            textDecoration: "none",
          }}
        >
          ← Try a PR receipt
        </Link>
        <Link
          href="/wall"
          style={{
            padding: "10px 18px",
            background: "#fff",
            border: "1px solid #e5e7eb",
            color: "#374151",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            textDecoration: "none",
          }}
        >
          See the Wall of Shame
        </Link>
      </div>
    </main>
  );
}
