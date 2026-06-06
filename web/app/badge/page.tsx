import Link from "next/link";
import { TrackView } from "@/components/TrackView";

export const metadata = {
  title: "Honesty Badge — RoboTruth",
  description:
    "Drop a one-line badge in your README that shows your repo's RoboTruth honesty score. Self-updating, deterministic, no auth required.",
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "https://robotruth.vercel.app";

const EXAMPLES = [
  { owner: "facebook", name: "react" },
  { owner: "vercel", name: "next.js" },
  { owner: "rust-lang", name: "rust" },
];

function Snippet({ children }: { children: string }) {
  return (
    <pre
      style={{
        margin: "10px 0 0",
        padding: "12px 14px",
        background: "#0f172a",
        color: "#e2e8f0",
        borderRadius: 8,
        fontSize: 13,
        fontFamily: "var(--mono)",
        overflowX: "auto",
        lineHeight: 1.55,
      }}
    >
      {children}
    </pre>
  );
}

export default function BadgePage() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px" }}>
      <TrackView event="badge_view" />
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
        The Receipts Protocol · embeddable
      </div>
      <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em", margin: 0 }}>
        Honesty Badge
      </h1>
      <p style={{ color: "#4b5563", marginTop: 10, fontSize: 16, lineHeight: 1.55 }}>
        One line in your README. Self-updating. Deterministic. Shows the share of your
        repo&apos;s last 8 PRs grading A or B. No accounts. No webhook. No tokens.
      </p>

      <h2 style={{ marginTop: 36, fontSize: 18 }}>Markdown</h2>
      <Snippet>{`![RoboTruth](${API_BASE}/api/badge/OWNER/REPO.svg)`}</Snippet>

      <h2 style={{ marginTop: 28, fontSize: 18 }}>HTML</h2>
      <Snippet>{`<img src="${API_BASE}/api/badge/OWNER/REPO.svg" alt="RoboTruth honesty" />`}</Snippet>

      <h2 style={{ marginTop: 28, fontSize: 18 }}>Linked to your scorecard</h2>
      <Snippet>{`[![RoboTruth](${API_BASE}/api/badge/OWNER/REPO.svg)](https://robotruth-rdft.vercel.app/repo/OWNER/REPO)`}</Snippet>

      <h2 style={{ marginTop: 40, fontSize: 18 }}>Live examples</h2>
      <p style={{ color: "#6b7280", fontSize: 14, marginTop: 6 }}>
        Each badge is generated on demand from the audited PRs.
      </p>
      <ul style={{ listStyle: "none", padding: 0, marginTop: 14 }}>
        {EXAMPLES.map((ex) => (
          <li
            key={`${ex.owner}/${ex.name}`}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "10px 0",
              borderBottom: "1px solid #f3f4f6",
            }}
          >
            <img
              src={`${API_BASE}/api/badge/${ex.owner}/${ex.name}.svg`}
              alt={`RoboTruth · ${ex.owner}/${ex.name}`}
              height={20}
              style={{ display: "block" }}
            />
            <code style={{ fontSize: 13, color: "#374151" }}>
              {ex.owner}/{ex.name}
            </code>
            <Link
              href={`/repo/${ex.owner}/${ex.name}`}
              style={{ marginLeft: "auto", color: "#2563eb", fontSize: 13, textDecoration: "none" }}
            >
              view scorecard →
            </Link>
          </li>
        ))}
      </ul>

      <h2 style={{ marginTop: 40, fontSize: 18 }}>How the score is computed</h2>
      <p style={{ color: "#374151", fontSize: 14, lineHeight: 1.65 }}>
        We audit the last 8 PRs on the default branch and count what fraction grade{" "}
        <strong>A</strong> or <strong>B</strong> (HONEST or MOSTLY HONEST). The badge color
        ramps from red (&lt;25%) through yellow to green (≥90%). When the audit can&apos;t
        run — private repo, missing repo, GitHub rate-limit — the badge says{" "}
        <code>unverified</code> instead of lying with a 0%.
      </p>

      <p
        style={{
          marginTop: 28,
          padding: "12px 16px",
          background: "#f9fafb",
          border: "1px solid #e5e7eb",
          borderRadius: 10,
          fontSize: 13,
          color: "#374151",
        }}
      >
        <strong>Cache:</strong> badges are cached for an hour at the edge with
        stale-while-revalidate for a day. Re-paste your repo on{" "}
        <Link href="/" style={{ color: "#2563eb" }}>the front page</Link> to refresh sooner.
      </p>

      <p style={{ marginTop: 28, fontSize: 13, color: "#6b7280" }}>
        Want the embed inside your PR template instead?{" "}
        <Link href="/repo/facebook/react" style={{ color: "#374151", textDecoration: "underline" }}>
          See a live per-repo scorecard
        </Link>
        .
      </p>
    </main>
  );
}
