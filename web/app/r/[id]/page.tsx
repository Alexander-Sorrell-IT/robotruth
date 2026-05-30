import { getReceipt } from "@/lib/api";
import { ReceiptCard } from "@/components/ReceiptCard";

// Next.js 16: params is a Promise
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let title = "RoboTruth receipt";
  let description =
    "A deterministic receipt of what an AI-written PR claimed vs what it actually did. No model in the verdict path.";
  try {
    const r = await getReceipt(id);
    const und = r.undisclosed?.length ?? 0;
    const unh = r.unhonored?.length ?? 0;
    const del = r.delivered?.length ?? 0;
    const prLabel = r.pr ? `${r.pr.repo} #${r.pr.number}` : "Direct diff";
    title = `${r.verdict} · grade ${r.grade} · ${prLabel}`;
    // Verdict-specific description so the OG preview tells the story even
    // before the image renders — and so Slack/Discord text-only unfurls work.
    const parts: string[] = [];
    if (und > 0) parts.push(`${und} undisclosed`);
    if (unh > 0) parts.push(`${unh} unhonored`);
    if (del > 0) parts.push(`${del} delivered`);
    const counts = parts.length > 0 ? parts.join(" · ") : "0 flags raised";
    const prTitle = r.pr?.title ?? "Pasted diff";
    description = `${r.verdict} · ${prTitle} — ${counts}. Deterministic receipt · no model in the verdict path.`;
  } catch {
    // receipt not found — use defaults
  }
  const img = `/api/og?id=${encodeURIComponent(id)}`;
  return {
    title,
    description,
    openGraph: { title, description, images: [img] },
    twitter: { card: "summary_large_image", title, description, images: [img] },
  };
}

export default async function ReceiptPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let receipt;
  try { receipt = await getReceipt(id); }
  catch { return <main style={{ padding: 40 }}>Receipt not found.</main>; }
  return (
    <main style={{ padding: "40px 16px" }}>
      <ReceiptCard receipt={receipt} id={id} />
    </main>
  );
}
