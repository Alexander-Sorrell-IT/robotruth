import type { Receipt, Flag } from "@/lib/receipt";
import { ClaimsEditor } from "@/components/ClaimsEditor";
import { CopyLinkButton } from "@/components/CopyLinkButton";
import Link from "next/link";

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

function Bucket({
  title,
  icon,
  accentColor,
  flags,
}: {
  title: string;
  icon: string;
  accentColor: string;
  flags: Flag[];
}) {
  if (flags.length === 0) return null;
  return (
    <div
      style={{
        marginTop: 16,
        borderLeft: `3px solid ${accentColor}`,
        paddingLeft: 12,
      }}
    >
      <h3
        style={{
          margin: 0,
          fontSize: 11,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.07em",
          color: accentColor,
        }}
      >
        {icon} {title}
      </h3>
      <ul style={{ margin: "8px 0 0", paddingLeft: 0, listStyle: "none" }}>
        {flags.map((f, i) => (
          <li
            key={i}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
              gap: 8,
              padding: "4px 0",
              borderBottom: i < flags.length - 1 ? "1px solid #f3f4f6" : "none",
            }}
          >
            <span style={{ fontSize: 13, color: "#111827" }}>{f.label}</span>
            {f.file && (
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
                {f.line ? `:${f.line}` : ""}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ReceiptCard({ receipt }: { receipt: Receipt }) {
  const c = VERDICT_COLOR[receipt.verdict] ?? "#444";
  const bg = VERDICT_BG[receipt.verdict] ?? "#f9fafb";

  return (
    <div
      style={{
        maxWidth: 640,
        margin: "0 auto",
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 16,
        boxShadow: "0 4px 24px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid #f3f4f6",
        }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "#9ca3af",
          }}
        >
          RoboTruth · INTENT RECEIPT &nbsp;·&nbsp; {receipt.pr.repo} #{receipt.pr.number}
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
          {receipt.pr.title}
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
            background: `${c}18`,
            color: c,
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
            background: `${c}18`,
            color: c,
            fontSize: 28,
            fontWeight: 800,
          }}
        >
          {receipt.grade}
        </span>
      </div>

      {/* Buckets */}
      <div style={{ padding: "8px 24px 4px" }}>
        <Bucket
          title="Did, but didn't mention"
          icon="⚠️"
          accentColor="#ea580c"
          flags={receipt.undisclosed}
        />
        <Bucket
          title="Claimed, but not found"
          icon="❌"
          accentColor="#dc2626"
          flags={receipt.unhonored}
        />
        <Bucket
          title="Claimed & delivered"
          icon="✅"
          accentColor="#16a34a"
          flags={receipt.delivered}
        />
      </div>

      {/* Claims editor */}
      <div style={{ padding: "0 24px" }}>
        <ClaimsEditor
          prUrl={receipt.pr.url}
          parsedClaims={receipt.parsed_claims}
          claimKinds={receipt.claim_kinds}
        />
      </div>

      {/* Footer */}
      <div
        style={{
          padding: "16px 24px",
          borderTop: "1px solid #f3f4f6",
          marginTop: 8,
        }}
      >
        <div
          style={{
            fontSize: 11,
            color: "#9ca3af",
            marginBottom: 12,
          }}
        >
          Deterministic · every flag cites file:line · no AI opinions &nbsp;·&nbsp; {receipt.math}
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <Link
            href="/"
            style={{
              padding: "8px 16px",
              borderRadius: 8,
              background: "#111827",
              color: "#fff",
              fontSize: 14,
              fontWeight: 500,
            }}
          >
            Audit your own →
          </Link>
          <CopyLinkButton />
        </div>
      </div>
    </div>
  );
}
