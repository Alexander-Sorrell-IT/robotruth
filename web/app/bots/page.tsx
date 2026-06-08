import Link from "next/link";
import { TrackView } from "@/components/TrackView";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

interface BotEntry {
  name: string;
  emoji: string;
  score: number;
  total: number;
  verdicts: { HONEST: number; "MOSTLY HONEST": number; SNEAKY: number; LIAR: number };
  note: string;
}

interface BotsResponse {
  bots: BotEntry[];
  seeded: boolean;
  note: string;
}

async function getBots(): Promise<BotsResponse> {
  try {
    const r = await fetch(`${BASE}/api/bots`, { cache: "no-store" });
    if (!r.ok) return { bots: [], seeded: false, note: "" };
    return (await r.json()) as BotsResponse;
  } catch {
    return { bots: [], seeded: false, note: "" };
  }
}

function scoreColor(score: number): string {
  if (score >= 80) return "#16a34a";
  if (score >= 60) return "#ca8a04";
  if (score >= 40) return "#ea580c";
  return "#dc2626";
}

export const metadata = { title: "Bot Leaderboard — RoboTruth" };

export default async function BotsPage() {
  const { bots, note } = await getBots();
  const sorted = [...bots].sort((a, b) => b.score - a.score);

  return (
    <main
      style={{
        maxWidth: 720,
        margin: "0 auto",
        padding: "48px 16px",
      }}
    >
      <TrackView event="bots_view" />
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
        The Receipts Protocol · bot rankings
      </div>
      <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em", margin: 0 }}>
        AI Agent Honesty Leaderboard
      </h1>
      <p style={{ color: "#4b5563", marginTop: 10, fontSize: 16, lineHeight: 1.55 }}>
        Which bots tell the truth? Ranked by honesty score across audited PRs.
      </p>
      <p style={{ color: "#6b7280", marginTop: 6, fontSize: 13 }}>
        Scores estimated from corpus sample · updates when GITHUB_TOKEN is configured
      </p>

      {note && (
        <div
          style={{
            marginTop: 16,
            padding: "10px 14px",
            borderRadius: 8,
            background: "#fffbeb",
            border: "1px solid #fde68a",
            fontSize: 13,
            color: "#92400e",
          }}
        >
          {note}
        </div>
      )}

      <ul style={{ listStyle: "none", padding: 0, marginTop: 28 }}>
        {sorted.map((bot, i) => {
          const total =
            bot.verdicts.HONEST +
            bot.verdicts["MOSTLY HONEST"] +
            bot.verdicts.SNEAKY +
            bot.verdicts.LIAR;
          const pct = (n: number) => (total > 0 ? (n / total) * 100 : 0);
          const color = scoreColor(bot.score);

          return (
            <li
              key={bot.name}
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                padding: "18px 20px",
                marginBottom: 12,
                background: "#fff",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
                {/* Rank */}
                <span
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: "#6b7280",
                    minWidth: 28,
                    flexShrink: 0,
                  }}
                >
                  #{i + 1}
                </span>

                {/* Emoji + name */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <span style={{ fontSize: 20, marginRight: 8 }}>{bot.emoji}</span>
                  <span
                    style={{
                      fontSize: 16,
                      fontWeight: 700,
                      color: "#111827",
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {bot.name}
                  </span>
                </div>

                {/* Score */}
                <span
                  style={{
                    fontSize: 28,
                    fontWeight: 800,
                    color,
                    letterSpacing: "-0.03em",
                    flexShrink: 0,
                  }}
                >
                  {bot.score}%
                </span>
              </div>

              {/* Verdict distribution bar */}
              <div
                style={{
                  marginTop: 14,
                  height: 8,
                  borderRadius: 4,
                  overflow: "hidden",
                  display: "flex",
                  background: "#f3f4f6",
                }}
              >
                {pct(bot.verdicts.HONEST) > 0 && (
                  <div
                    style={{
                      width: `${pct(bot.verdicts.HONEST)}%`,
                      background: "#16a34a",
                    }}
                    title={`HONEST: ${bot.verdicts.HONEST}`}
                  />
                )}
                {pct(bot.verdicts["MOSTLY HONEST"]) > 0 && (
                  <div
                    style={{
                      width: `${pct(bot.verdicts["MOSTLY HONEST"])}%`,
                      background: "#84cc16",
                    }}
                    title={`MOSTLY HONEST: ${bot.verdicts["MOSTLY HONEST"]}`}
                  />
                )}
                {pct(bot.verdicts.SNEAKY) > 0 && (
                  <div
                    style={{
                      width: `${pct(bot.verdicts.SNEAKY)}%`,
                      background: "#ea580c",
                    }}
                    title={`SNEAKY: ${bot.verdicts.SNEAKY}`}
                  />
                )}
                {pct(bot.verdicts.LIAR) > 0 && (
                  <div
                    style={{
                      width: `${pct(bot.verdicts.LIAR)}%`,
                      background: "#dc2626",
                    }}
                    title={`LIAR: ${bot.verdicts.LIAR}`}
                  />
                )}
              </div>

              {/* Bar legend */}
              <div
                style={{
                  marginTop: 6,
                  display: "flex",
                  gap: 14,
                  flexWrap: "wrap",
                  fontSize: 11,
                  color: "#6b7280",
                }}
              >
                <span>
                  <span style={{ color: "#16a34a", fontWeight: 600 }}>■</span> HONEST{" "}
                  {bot.verdicts.HONEST}
                </span>
                <span>
                  <span style={{ color: "#84cc16", fontWeight: 600 }}>■</span> MOSTLY HONEST{" "}
                  {bot.verdicts["MOSTLY HONEST"]}
                </span>
                <span>
                  <span style={{ color: "#ea580c", fontWeight: 600 }}>■</span> SNEAKY{" "}
                  {bot.verdicts.SNEAKY}
                </span>
                <span>
                  <span style={{ color: "#dc2626", fontWeight: 600 }}>■</span> LIAR{" "}
                  {bot.verdicts.LIAR}
                </span>
              </div>

              {/* Note */}
              {bot.note && (
                <p
                  style={{
                    marginTop: 10,
                    fontSize: 12,
                    color: "#6b7280",
                    margin: "10px 0 0",
                    lineHeight: 1.5,
                  }}
                >
                  {bot.note}
                </p>
              )}
            </li>
          );
        })}
      </ul>

      <p style={{ marginTop: 36, fontSize: 13, color: "#6b7280" }}>
        See the worst catches on the{" "}
        <Link href="/wall" style={{ color: "#6b7280", textDecoration: "underline" }}>
          Wall of Shame
        </Link>
        {" · "}
        <Link href="/" style={{ color: "#6b7280", textDecoration: "underline" }}>
          Submit a PR URL
        </Link>
      </p>
    </main>
  );
}
