import { Fragment, type ReactNode } from "react";
import Link from "next/link";
import { CopyYamlButton } from "./CopyYamlButton";
import { TrackView } from "@/components/TrackView";

export const metadata = {
  title: "GitHub Action — RoboTruth",
  description:
    "Audit every PR your AI agent opens. Get a receipt before it merges. One YAML snippet, no API key required.",
};

const YAML = `name: RoboTruth Audit

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  robotruth:
    runs-on: ubuntu-latest
    steps:
      - name: Audit PR with RoboTruth
        run: |
          pip install httpx --quiet
          python - <<'EOF'
          import httpx, os, sys
          url = os.environ["PR_URL"]
          r = httpx.post(
            "https://robotruth.vercel.app/api/audit",
            json={"url": url},
            timeout=60,
          )
          d = r.json()["receipt"]
          print(f"RoboTruth: {d['verdict']} · Grade {d['grade']}")
          print(f"  {d['math']}")
          if d["undisclosed"]:
            for f in d["undisclosed"]:
              print(f"  ⚠ {f['label']} — {f.get('file','')}:{f.get('line','')}")
          sys.exit(0 if d["grade"] in ("A", "B") else 1)
          EOF
        env:
          PR_URL: \${{ github.event.pull_request.html_url }}`;

// github-dark-ish palette for the hero snippet.
const HL = {
  comment: "#8b949e",
  string: "#a5d6ff",
  number: "#79c0ff",
  keyword: "#ff7b72",
  key: "#7ee787",
  punct: "#e2e8f0",
};

// Python keywords that appear in the heredoc body.
const PY_KEYWORDS = new Set([
  "import",
  "for",
  "in",
  "if",
  "else",
  "print",
  "os",
  "sys",
  "httpx",
]);

// Tasteful, text-preserving tokenizer. Ordered: strings first so keywords inside
// strings are not re-colored; a final catch-all guarantees every character is
// emitted, so the rendered text always equals the raw YAML string.
const TOKEN = new RegExp(
  [
    "(#[^\\n]*)", // 1: comment
    "(\"(?:[^\"\\\\]|\\\\.)*\"|'(?:[^'\\\\]|\\\\.)*')", // 2: string
    "(\\b\\d+\\b)", // 3: number
    "([A-Za-z_][A-Za-z0-9_-]*)(?=:)", // 4: yaml/mapping key (word before a colon)
    "([A-Za-z_][A-Za-z0-9_]*)", // 5: identifier (may be a python keyword)
    "([\\s\\S])", // 6: catch-all (any single char incl. whitespace/punct)
  ].join("|"),
  "g",
);

function highlightLine(line: string, lineKey: number): ReactNode {
  const nodes: ReactNode[] = [];
  let m: RegExpExecArray | null;
  let i = 0;
  TOKEN.lastIndex = 0;
  while ((m = TOKEN.exec(line)) !== null) {
    const key = `${lineKey}-${i++}`;
    if (m[1] !== undefined) {
      nodes.push(
        <span key={key} style={{ color: HL.comment }}>
          {m[1]}
        </span>,
      );
    } else if (m[2] !== undefined) {
      nodes.push(
        <span key={key} style={{ color: HL.string }}>
          {m[2]}
        </span>,
      );
    } else if (m[3] !== undefined) {
      nodes.push(
        <span key={key} style={{ color: HL.number }}>
          {m[3]}
        </span>,
      );
    } else if (m[4] !== undefined) {
      nodes.push(
        <span key={key} style={{ color: HL.key }}>
          {m[4]}
        </span>,
      );
    } else if (m[5] !== undefined) {
      if (PY_KEYWORDS.has(m[5])) {
        nodes.push(
          <span key={key} style={{ color: HL.keyword }}>
            {m[5]}
          </span>,
        );
      } else {
        nodes.push(m[5]);
      }
    } else {
      // catch-all char: whitespace and punctuation, kept verbatim
      nodes.push(m[6]);
    }
  }
  return nodes;
}

function highlightYaml(src: string): ReactNode[] {
  const lines = src.split("\n");
  return lines.map((line, idx) => (
    <Fragment key={idx}>
      {highlightLine(line, idx)}
      {idx < lines.length - 1 ? "\n" : null}
    </Fragment>
  ));
}

export default function GitHubActionPage() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px 80px" }}>
      <TrackView event="github_action_view" />
      {/* Eyebrow */}
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
        The Receipts Protocol · CI integration
      </div>

      {/* Header */}
      <h1
        style={{
          fontSize: 36,
          fontWeight: 800,
          letterSpacing: "-0.025em",
          lineHeight: 1.1,
          margin: 0,
          color: "#111827",
        }}
      >
        Install RoboTruth in CI
      </h1>
      <p
        style={{
          marginTop: 12,
          fontSize: 18,
          color: "#4b5563",
          lineHeight: 1.5,
          fontWeight: 500,
        }}
      >
        Audit every PR your AI agent opens. Get a receipt before it merges.
      </p>

      {/* Code block */}
      <div style={{ marginTop: 32, position: "relative" }}>
        <pre
          style={{
            margin: 0,
            padding: "20px 20px 20px",
            background: "#0f172a",
            color: "#e2e8f0",
            borderRadius: 10,
            fontSize: 13,
            fontFamily: "var(--mono, ui-monospace, 'Cascadia Code', monospace)",
            overflowX: "auto",
            lineHeight: 1.6,
            whiteSpace: "pre",
          }}
        >
          <code style={{ color: HL.punct }}>{highlightYaml(YAML)}</code>
        </pre>
        <div style={{ marginTop: 10, display: "flex", justifyContent: "flex-end" }}>
          <CopyYamlButton yaml={YAML} />
        </div>
      </div>

      {/* What it does */}
      <h2
        style={{
          marginTop: 40,
          fontSize: 18,
          fontWeight: 700,
          color: "#111827",
          letterSpacing: "-0.01em",
        }}
      >
        What it does
      </h2>
      <ul
        style={{
          marginTop: 12,
          padding: 0,
          listStyle: "none",
          display: "flex",
          flexDirection: "column",
          gap: 10,
        }}
      >
        {[
          "Fires on every PR open and sync — no manual trigger needed.",
          "POSTs to the RoboTruth API. No API key required for public repos.",
          "Exits 1 if the grade is D or F, blocking merge when branch protection is on.",
        ].map((text, i) => (
          <li
            key={i}
            style={{
              display: "flex",
              gap: 10,
              fontSize: 15,
              color: "#374151",
              lineHeight: 1.55,
            }}
          >
            <span
              style={{
                flexShrink: 0,
                width: 22,
                height: 22,
                borderRadius: "50%",
                background: "#111827",
                color: "#fff",
                fontSize: 12,
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginTop: 1,
              }}
            >
              {i + 1}
            </span>
            <span>{text}</span>
          </li>
        ))}
      </ul>

      {/* Note */}
      <p
        style={{
          marginTop: 28,
          padding: "12px 16px",
          background: "#f9fafb",
          border: "1px solid #e5e7eb",
          borderRadius: 10,
          fontSize: 13,
          color: "#374151",
          lineHeight: 1.6,
        }}
      >
        <strong>Note:</strong> The action POSTs to the public RoboTruth API. No API key required
        for public repos.
      </p>

      {/* Nav links */}
      <div
        style={{
          marginTop: 36,
          display: "flex",
          gap: 20,
          fontSize: 14,
          color: "#6b7280",
        }}
      >
        <Link href="/" style={{ color: "#374151", textDecoration: "underline" }}>
          ← Home
        </Link>
        <Link href="/badge" style={{ color: "#374151", textDecoration: "underline" }}>
          Honesty Badge →
        </Link>
      </div>
    </main>
  );
}
