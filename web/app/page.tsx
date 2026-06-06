"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auditUrl } from "@/lib/api";
import { track } from "@/lib/analytics";

const LOADING_MESSAGES = [
  "Reading PR…",
  "Parsing diff…",
  "Running 4 scanners…",
  "Grading…",
];

interface ReceiptExample {
  id: string;
  verdict: "LIAR" | "SNEAKY" | "HONEST";
  grade: string;
  label: string;
  bot: string;
}

const RECEIPT_EXAMPLES: ReceiptExample[] = [
  {
    id: "svRkjwJn",
    verdict: "LIAR",
    grade: "F",
    label: "feat: add user analytics — adds tests, no dependency changes",
    bot: "copilot-bot",
  },
  {
    id: "qtEkeLMq",
    verdict: "LIAR",
    grade: "F",
    label: "chore: update deps — only touches package.json",
    bot: "renovate-bot",
  },
  {
    id: "VNQdNhA7",
    verdict: "HONEST",
    grade: "A",
    label: "feat: add dark mode toggle",
    bot: "human-dev",
  },
];

const VERDICT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  LIAR: { bg: "#fef2f2", text: "#dc2626", border: "#fecaca" },
  SNEAKY: { bg: "#fffbeb", text: "#d97706", border: "#fde68a" },
  HONEST: { bg: "#f0fdf4", text: "#16a34a", border: "#bbf7d0" },
};

export default function Home() {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [loadingMsgIdx, setLoadingMsgIdx] = useState(0);
  const router = useRouter();

  useEffect(() => {
    track("landing_view");
  }, []);

  useEffect(() => {
    if (!busy) return;
    setLoadingMsgIdx(0);
    const interval = setInterval(() => {
      setLoadingMsgIdx((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 1500);
    return () => clearInterval(interval);
  }, [busy]);

  async function run(target: string) {
    setBusy(true);
    setErr("");
    try {
      const { id, receipt } = await auditUrl(target);
      track("receipt_generated", { id });
      if (typeof window !== "undefined" && window.pendo) {
        window.pendo.track("pr_audited", {
          receiptId: id,
          verdict: receipt.verdict,
          grade: receipt.grade,
          flagCount: (receipt.undisclosed?.length ?? 0) + (receipt.unhonored?.length ?? 0),
          undisclosedCount: receipt.undisclosed?.length ?? 0,
          unhonoredCount: receipt.unhonored?.length ?? 0,
          deliveredCount: receipt.delivered?.length ?? 0,
          claimsParsedCount: receipt.parsed_claims?.length ?? 0,
          repo: receipt.pr?.repo ?? "",
          prNumber: receipt.pr?.number ?? 0,
        });
      }
      router.push("/r/" + id);
    } catch (e) {
      const errorMessage = (e as Error).message;
      setErr(errorMessage);
      if (typeof window !== "undefined" && window.pendo) {
        window.pendo.track("audit_failed", {
          prUrl: target,
          errorMessage: errorMessage.substring(0, 200),
        });
      }
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
          if (url.trim()) {
            track("pr_pasted");
            const trimmedUrl = url.trim();
            const prMatch = trimmedUrl.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/);
            if (typeof window !== "undefined" && window.pendo) {
              window.pendo.track("pr_url_submitted", {
                prUrl: trimmedUrl,
                repo: prMatch ? prMatch[1] : "",
                prNumber: prMatch ? parseInt(prMatch[2], 10) : 0,
              });
            }
            run(trimmedUrl);
          }
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
            minWidth: 120,
          }}
        >
          {busy ? LOADING_MESSAGES[loadingMsgIdx] : "Audit"}
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

      {/* Example receipt cards */}
      <div style={{ marginTop: 28 }}>
        <span style={{ fontSize: 13, color: "#9ca3af", display: "block", marginBottom: 10 }}>
          See it in action:
        </span>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 10,
          }}
        >
          {RECEIPT_EXAMPLES.map((ex) => {
            const colors = VERDICT_COLORS[ex.verdict] ?? VERDICT_COLORS.HONEST;
            return (
              <button
                key={ex.id}
                onClick={() => {
                  track("example_clicked", { id: ex.id, verdict: ex.verdict });
                  router.push("/r/" + ex.id);
                }}
                style={{
                  background: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: 10,
                  padding: "14px 12px",
                  textAlign: "left",
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                  transition: "border-color 0.15s, box-shadow 0.15s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "#6b7280";
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = "0 1px 4px rgba(0,0,0,0.08)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "#e5e7eb";
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = "none";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      padding: "2px 7px",
                      borderRadius: 4,
                      background: colors.bg,
                      color: colors.text,
                      border: `1px solid ${colors.border}`,
                      letterSpacing: "0.04em",
                    }}
                  >
                    {ex.verdict}
                  </span>
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 800,
                      color: colors.text,
                      background: colors.bg,
                      border: `1px solid ${colors.border}`,
                      borderRadius: 4,
                      padding: "2px 6px",
                    }}
                  >
                    {ex.grade}
                  </span>
                </div>
                <div style={{ fontSize: 11, color: "#6b7280", fontWeight: 500 }}>
                  {ex.bot}
                </div>
                <div style={{ fontSize: 12, color: "#374151", lineHeight: 1.4 }}>
                  {ex.label}
                </div>
                <div style={{ fontSize: 12, color: "#2563eb", fontWeight: 500, marginTop: 2 }}>
                  Load receipt →
                </div>
              </button>
            );
          })}
        </div>
      </div>

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

      {/* Footer links */}
      <p style={{ marginTop: 24, fontSize: 13, color: "#9ca3af" }}>
        See the worst offenders on the{" "}
        <Link href="/wall" style={{ color: "#6b7280", textDecoration: "underline" }}>
          Wall of Shame
        </Link>
        {" · "}
        <Link href="/bots" style={{ color: "#6b7280", textDecoration: "underline" }}>
          Bot Leaderboard
        </Link>
        {" · "}
        <Link href="/github-action" style={{ color: "#6b7280", textDecoration: "underline" }}>
          GitHub Action
        </Link>
      </p>
    </main>
  );
}
