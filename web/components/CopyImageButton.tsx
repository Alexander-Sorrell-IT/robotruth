"use client";
import { useState } from "react";
import { track } from "@/lib/analytics";

export function CopyImageButton({ id }: { id: string }) {
  const [state, setState] = useState<"idle" | "copying" | "done" | "error">("idle");

  async function copy() {
    setState("copying");
    try {
      const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
      const res = await fetch(`${BASE}/api/og?id=${encodeURIComponent(id)}`);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      track("image_copied", { id });
      if (typeof window !== "undefined" && window.pendo) {
        window.pendo.track("receipt_image_copied", {
          receiptId: id,
        });
      }
      setState("done");
      setTimeout(() => setState("idle"), 2000);
    } catch (e) {
      if (typeof window !== "undefined" && window.pendo) {
        window.pendo.track("receipt_image_copy_failed", {
          receiptId: id,
          errorMessage: (e instanceof Error ? e.message : "Unknown error").substring(0, 200),
        });
      }
      setState("error");
      setTimeout(() => setState("idle"), 2000);
    }
  }

  return (
    <button
      onClick={copy}
      disabled={state === "copying"}
      style={{
        padding: "8px 16px",
        borderRadius: 8,
        background: "#f9fafb",
        border: "1px solid #e5e7eb",
        color: "#374151",
        fontSize: 14,
        fontWeight: 500,
        cursor: state === "copying" ? "wait" : "pointer",
      }}
    >
      {state === "idle" && "Copy image"}
      {state === "copying" && "Copying…"}
      {state === "done" && "Image copied!"}
      {state === "error" && "Copy failed"}
    </button>
  );
}
