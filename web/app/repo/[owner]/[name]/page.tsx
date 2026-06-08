import { TrackView } from "@/components/TrackView";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const COLOR: Record<string, string> = { HONEST: "#16a34a", "MOSTLY HONEST": "#65a30d", SNEAKY: "#ea580c", LIAR: "#dc2626" };

interface Item { number: number; title: string; verdict: string; grade: string; url: string; }
interface Scorecard { repo: string; score: number | null; items: Item[]; }

async function getScore(owner: string, name: string): Promise<Scorecard | null> {
  try {
    const r = await fetch(`${BASE}/api/repo/${owner}/${name}`, { cache: "no-store" });
    if (!r.ok) return null;
    return (await r.json()) as Scorecard;
  } catch {
    return null;
  }
}

export default async function RepoPage({ params }: { params: Promise<{ owner: string; name: string }> }) {
  const { owner, name } = await params;
  const data = await getScore(owner, name);
  if (!data) return <main style={{ padding: 40 }}>Couldn&apos;t score {owner}/{name}.</main>;
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "48px 16px" }}>
      <TrackView event="repo_scorecard_view" props={{ owner, name }} />
      <h1 style={{ fontSize: 28, fontWeight: 800 }}>{data.repo}</h1>
      <p style={{ fontSize: 18 }}>AI-honesty score: <strong>{data.score !== null ? `${data.score}%` : "unverified"}</strong> <span style={{ color: "#6b7280" }}>(recent PRs graded A/B)</span></p>
      <ul style={{ listStyle: "none", padding: 0, marginTop: 16 }}>
        {data.items.map((it) => (
          <li key={it.number} style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 14, marginBottom: 10 }}>
            <a href={it.url} target="_blank" rel="noreferrer" style={{ textDecoration: "none", color: "inherit" }}>
              <span style={{ fontWeight: 700, color: COLOR[it.verdict] ?? "#444" }}>{it.verdict} · {it.grade}</span>
              <span style={{ color: "#6b7280" }}> — #{it.number}</span>
              <div style={{ marginTop: 4 }}>{it.title}</div>
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}
