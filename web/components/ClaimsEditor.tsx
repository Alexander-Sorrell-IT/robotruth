"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { auditUrl } from "@/lib/api";

export function ClaimsEditor({ prUrl, parsedClaims, claimKinds }: { prUrl: string; parsedClaims: string[]; claimKinds: string[] }) {
  const [keep, setKeep] = useState<boolean[]>(parsedClaims.map(() => true));
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  if (parsedClaims.length === 0) return null;
  const changed = keep.some((k) => !k);
  async function reaudit() {
    setBusy(true);
    try {
      const kinds = claimKinds.filter((_, i) => keep[i]);
      const removedCount = claimKinds.length - kinds.length;
      const { id, receipt } = await auditUrl(prUrl, kinds);
      if (typeof window !== "undefined" && window.pendo) {
        window.pendo.track("claims_reaudited", {
          prUrl,
          originalClaimCount: claimKinds.length,
          keptClaimCount: kinds.length,
          removedClaimCount: removedCount,
          newReceiptId: id,
          newVerdict: receipt.verdict,
          newGrade: receipt.grade,
        });
      }
      router.push(`/r/${id}`);
    } finally { setBusy(false); }
  }
  return (
    <div style={{ marginTop: 16, fontSize: 13, color: "#374151" }}>
      <div style={{ color: "#6b7280" }}>We read this PR as promising — untick anything we misread:</div>
      {parsedClaims.map((c, i) => (
        <label key={i} style={{ display: "block", marginTop: 4 }}>
          <input type="checkbox" checked={keep[i]} onChange={() => setKeep((p) => p.map((v, j) => (j === i ? !v : v)))} /> {c}
        </label>
      ))}
      {changed && (
        <button onClick={reaudit} disabled={busy} style={{ marginTop: 8, padding: "6px 12px", borderRadius: 6, border: "1px solid #d1d5db", cursor: "pointer" }}>
          {busy ? "Re-auditing…" : "Re-audit with corrected claims"}
        </button>
      )}
    </div>
  );
}
