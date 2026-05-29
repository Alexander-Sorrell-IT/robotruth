import type { Receipt } from "./receipt";
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function auditUrl(url: string, keepClaimKinds?: string[]): Promise<{ id: string; receipt: Receipt }> {
  const r = await fetch(`${BASE}/api/audit`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ url, keep_claim_kinds: keepClaimKinds ?? null }),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? `Audit failed (${r.status})`);
  return r.json();
}

export async function getReceipt(id: string): Promise<Receipt> {
  const r = await fetch(`${BASE}/api/receipt/${id}`, { cache: "no-store" });
  if (!r.ok) throw new Error("Receipt not found");
  const d = (await r.json()) as Receipt;
  // Defensive: the render path (ReceiptCard, ClaimsEditor) assumes these are
  // always arrays. A partial/malformed receipt with a missing/null list would
  // otherwise crash the page instead of showing a clean state.
  d.delivered ??= [];
  d.undisclosed ??= [];
  d.unhonored ??= [];
  d.parsed_claims ??= [];
  d.claim_kinds ??= [];
  return d;
}
