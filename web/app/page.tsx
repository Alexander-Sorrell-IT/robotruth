"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { auditUrl } from "@/lib/api";

const EXAMPLES: string[] = [];  // real seed PRs filled in Plan 3

export default function Home() {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();

  async function run(target: string) {
    setBusy(true); setErr("");
    try { const { id } = await auditUrl(target); router.push(`/r/${id}`); }
    catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <main style={{ maxWidth: 640, margin: "0 auto", padding: "64px 16px", fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 34, fontWeight: 800 }}>Did the robot lie?</h1>
      <p style={{ color: "#4b5563" }}>Paste a public GitHub PR. See what it <em>claimed</em> vs. what it <em>actually did</em>.</p>
      <form onSubmit={(e) => { e.preventDefault(); if (url) run(url); }} style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Paste a public GitHub PR link"
               style={{ flex: 1, padding: 12, border: "1px solid #d1d5db", borderRadius: 8 }} />
        <button disabled={busy} style={{ padding: "12px 18px", borderRadius: 8, background: "#111827", color: "#fff", border: 0 }}>
          {busy ? "Reading…" : "Audit"}
        </button>
      </form>
      {err && <p style={{ color: "#dc2626" }}>{err}</p>}
      {EXAMPLES.length > 0 && (
        <p style={{ marginTop: 16, color: "#6b7280" }}>Try one:{" "}
          {EXAMPLES.map((e, i) => (
            <button key={i} onClick={() => run(e)} disabled={busy}
                    style={{ marginRight: 8, textDecoration: "underline", background: "none", border: 0, cursor: "pointer", color: "#2563eb" }}>
              example {i + 1}
            </button>
          ))}
        </p>
      )}
    </main>
  );
}
