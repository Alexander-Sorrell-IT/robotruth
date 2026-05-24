import { getReceipt } from "@/lib/api";
import { ReceiptCard } from "@/components/ReceiptCard";

// Next.js 16: params is a Promise
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let title = "RoboTruth receipt";
  try {
    const r = await getReceipt(id);
    title = `${r.verdict} · grade ${r.grade} · ${r.pr.repo} #${r.pr.number}`;
  } catch {
    // receipt not found — use default title
  }
  const img = `/api/og?id=${id}`;
  return {
    title,
    openGraph: { title, images: [img] },
    twitter: { card: "summary_large_image", title, images: [img] },
  };
}

export default async function ReceiptPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let receipt;
  try { receipt = await getReceipt(id); }
  catch { return <main style={{ padding: 40 }}>Receipt not found.</main>; }
  return (
    <main style={{ padding: "40px 16px" }}>
      <ReceiptCard receipt={receipt} />
    </main>
  );
}
