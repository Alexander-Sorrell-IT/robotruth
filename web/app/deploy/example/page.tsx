import Link from "next/link";

export const metadata = {
  title: "Deploy Receipt (preview) — RoboTruth",
  description:
    "The Receipts Protocol grammar applied to a deployment-agent claim. Same verdict words, same three buckets, same file:line citations. Preview of the next surface.",
};

const VERDICT_COLOR = "#ea580c"; // SNEAKY orange
const VERDICT_BG = "#fff7ed";

interface DeployFlag {
  label: string;
  resource: string;
  line?: string;
  severity: "critical" | "moderate" | "minor";
  evidence: string;
}

const UNDISCLOSED: DeployFlag[] = [
  {
    label: "Promoted to production (claimed: staging only)",
    resource: "argocd/app-prod.yaml",
    line: "syncPolicy.automated:true",
    severity: "critical",
    evidence: "+ syncPolicy:\n+   automated:\n+     prune: true",
  },
  {
    label: "New env var introduced without feature flag",
    resource: "k8s/deployment.yaml",
    line: "spec.template.spec.containers[0].env[+12]",
    severity: "moderate",
    evidence: "+ - name: DATABASE_POOL_SIZE\n+   value: \"32\"",
  },
  {
    label: "/health probe interval narrowed 30s → 5s",
    resource: "k8s/deployment.yaml",
    line: "livenessProbe.periodSeconds",
    severity: "moderate",
    evidence: "- periodSeconds: 30\n+ periodSeconds: 5",
  },
];

const UNHONORED: DeployFlag[] = [
  {
    label: "Claimed: 'no breaking changes' — narrowed probe interval breaks clients with cached config",
    resource: "k8s/deployment.yaml",
    severity: "moderate",
    evidence: "claim text: \"no breaking changes\"",
  },
];

const DELIVERED: DeployFlag[] = [
  {
    label: "Image tag bumped v2.3.0 → v2.3.1",
    resource: "k8s/deployment.yaml",
    line: "spec.template.spec.containers[0].image",
    severity: "minor",
    evidence: "+ image: app:v2.3.1",
  },
];

const SCANNERS = [
  "manifest_drift",
  "env_var_surface",
  "probe_changes",
  "rollout_target",
];

function Bucket({
  title,
  icon,
  color,
  flags,
}: {
  title: string;
  icon: string;
  color: string;
  flags: DeployFlag[];
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
                {f.resource}
                {f.line ? `:${f.line}` : ""}
              </span>
            </div>
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
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function DeployExamplePage() {
  const flagCount = UNDISCLOSED.length + UNHONORED.length;
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px" }}>
      {/* Preview banner */}
      <div
        style={{
          marginBottom: 24,
          padding: "12px 16px",
          background: "#fef3c7",
          border: "1px solid #fcd34d",
          borderRadius: 10,
          fontSize: 13,
          color: "#78350f",
          lineHeight: 1.5,
        }}
      >
        <strong>Preview · the next surface.</strong> This is the receipt grammar applied to a
        deploy-agent claim, with mocked data. Same verdict words. Same three buckets. Same{" "}
        <code style={{ background: "#fde68a", padding: "1px 5px", borderRadius: 4 }}>
          resource:line
        </code>{" "}
        evidence. <Link href="/" style={{ color: "#92400e", textDecoration: "underline" }}>
          The PR receipt
        </Link>{" "}
        is the same primitive aimed at a different surface.
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
            RoboTruth · DEPLOY RECEIPT &nbsp;·&nbsp; payments-api · release v2.3.1
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
            Roll out v2.3.1 — bugfix release, no breaking changes, staging only
          </div>
        </div>

        {/* Verdict block */}
        <div
          style={{
            padding: "20px 24px",
            background: VERDICT_BG,
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
              background: `${VERDICT_COLOR}18`,
              color: VERDICT_COLOR,
              fontSize: 20,
              fontWeight: 800,
              letterSpacing: "-0.01em",
            }}
          >
            SNEAKY
          </span>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: 48,
              height: 48,
              borderRadius: 10,
              background: `${VERDICT_COLOR}18`,
              color: VERDICT_COLOR,
              fontSize: 28,
              fontWeight: 800,
            }}
          >
            D
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
            <span style={{ color: "#ea580c" }}>●</span> Audit ran · {SCANNERS.length} scanners ·{" "}
            {flagCount} flag{flagCount === 1 ? "" : "s"} raised
          </div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "#9ca3af" }}>
            {SCANNERS.join(" · ")}
          </div>
        </div>

        {/* Buckets */}
        <div style={{ padding: "8px 24px 4px" }}>
          <Bucket title="Did, but didn't mention" icon="⚠️" color="#ea580c" flags={UNDISCLOSED} />
          <Bucket title="Claimed, but contradicted by deploy" icon="❌" color="#dc2626" flags={UNHONORED} />
          <Bucket title="Claimed & delivered" icon="✅" color="#16a34a" flags={DELIVERED} />
        </div>

        {/* Footer */}
        <div style={{ padding: "16px 24px", borderTop: "1px solid #f3f4f6", marginTop: 8 }}>
          <div style={{ fontSize: 11, color: "#9ca3af", marginBottom: 12 }}>
            Deterministic · every flag cites resource:path · no model in the verdict path &nbsp;·&nbsp;
            D: 1 critical + 2 moderate undisclosed, 1 unhonored; score=5
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
          A deploy receipt is the same primitive as a PR receipt: read the agent's claim, read
          the actual change, cite every divergence. The scanners are different (manifest drift,
          probe changes, rollout target, env var surface — instead of dangerous primitives,
          dependencies, scope drift, security guard) but the grammar is identical. One verdict
          word. One letter grade. Three buckets. Evidence at <code>resource:line</code>. No
          model in the verdict path.
        </p>
        <p style={{ margin: "12px 0 0", fontSize: 14, color: "#374151", lineHeight: 1.65 }}>
          PRs were the first surface because the diff is the ground truth and it's public.
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
