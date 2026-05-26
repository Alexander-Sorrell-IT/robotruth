"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auditUrl } from "@/lib/api";

const EXAMPLES: { url: string; label: string }[] = [
  { url: "https://github.com/rockgis/uiscloud_lightRAG/pull/6", label: "a dependabot bump" },
];

export default function Home() {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();

  async function run(target: string) {
    setBusy(true);
    setErr("");
    try {
      const { id } = await auditUrl(target);
      router.push(`/r/${id}`);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main
      style={{
        maxWidth: 640,
        margin: "0 auto",
        padding: "72px 24px 80px",
      }}
    >
      {/* Hero */}
      <div
        style={{
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: "#6b7280",
          marginBottom: 14,
        }}
      >
        The Receipts Protocol · first surface: GitHub PRs
      </div>
      <h1
        style={{
          fontSize: 46,
          fontWeight: 800,
          letterSpacing: "-0.03em",
          lineHeight: 1.05,
          color: "#111827",
        }}
      >
        Did the robot lie?
      </h1>
      <p
        style={{
          marginTop: 20,
          fontSize: 19,
          color: "#111827",
          lineHeight: 1.5,
          fontWeight: 500,
        }}
      >
        AI is now doing the work. Receipts make it impossible to lie about what it did.
      </p>
      <p
        style={{
          marginTop: 14,
          fontSize: 15,
          color: "#4b5563",
          lineHeight: 1.6,
        }}
      >
        Paste a public GitHub PR. In seconds, get a deterministic receipt — every divergence between what the AI <em>claimed</em> and what it <em>actually did</em>, cited at <code style={{ background: "#f3f4f6", padding: "1px 5px", borderRadius: 4, fontSize: 13 }}>file:line</code>.
        <strong style={{ color: "#111827" }}> No model in the verdict path.</strong>
      </p>

      {/* Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (url.trim()) run(url.trim());
        }}
        style={{ display: "flex", gap: 8, marginTop: 28 }}
      >
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo/pull/123"
          style={{
            flex: 1,
            padding: "13px 16px",
            border: "1px solid #d1d5db",
            borderRadius: 10,
            fontSize: 15,
            color: "#111827",
            background: "#fff",
            outline: "none",
          }}
        />
        <button
          disabled={busy}
          type="submit"
          style={{
            padding: "13px 22px",
            borderRadius: 10,
            background: busy ? "#374151" : "#111827",
            color: "#fff",
            border: 0,
            fontSize: 15,
            fontWeight: 600,
            cursor: busy ? "wait" : "pointer",
            whiteSpace: "nowrap",
            transition: "background 0.15s",
          }}
        >
          {busy ? "Reading…" : "Audit"}
        </button>
      </form>

      {/* Error */}
      {err && (
        <p
          style={{
            marginTop: 12,
            color: "#dc2626",
            fontSize: 14,
            padding: "10px 14px",
            background: "#fef2f2",
            borderRadius: 8,
            border: "1px solid #fecaca",
          }}
        >
          {err}
        </p>
      )}

      {/* Examples */}
      {EXAMPLES.length > 0 && (
        <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <span style={{ fontSize: 13, color: "#9ca3af" }}>Try one:</span>
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => run(ex.url)}
              disabled={busy}
              style={{
                fontSize: 13,
                color: "#2563eb",
                background: "#eff6ff",
                border: "1px solid #bfdbfe",
                borderRadius: 6,
                padding: "4px 10px",
                cursor: busy ? "wait" : "pointer",
                fontWeight: 500,
              }}
            >
              {ex.label}
            </button>
          ))}
        </div>
      )}

      {/* How it works */}
      <div
        style={{
          marginTop: 56,
          display: "flex",
          gap: 4,
          alignItems: "center",
          fontSize: 13,
          color: "#6b7280",
          flexWrap: "wrap",
        }}
      >
        <span style={{ fontWeight: 600, color: "#374151" }}>How it works:</span>
        <span>Paste a PR</span>
        <span style={{ color: "#d1d5db" }}>→</span>
        <span>We diff claims vs. reality</span>
        <span style={{ color: "#d1d5db" }}>→</span>
        <span>Get a shareable receipt</span>
      </div>

      {/* Wall link */}
      <p style={{ marginTop: 24, fontSize: 13, color: "#9ca3af" }}>
        See the worst offenders on the{" "}
        <Link href="/wall" style={{ color: "#6b7280", textDecoration: "underline" }}>
          Wall of Shame
        </Link>
        .
      </p>
    </main>
  );
}
