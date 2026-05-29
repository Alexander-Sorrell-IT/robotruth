"use client";
import { useState } from "react";
import { track } from "@/lib/analytics";

export function CopyLinkButton() {
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard.writeText(window.location.href).then(() => {
      track("receipt_shared");
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <button
      onClick={copy}
      style={{
        padding: "8px 16px",
        borderRadius: 8,
        border: "1px solid #e5e7eb",
        background: "#fff",
        color: "#374151",
        fontSize: 14,
        cursor: "pointer",
        fontWeight: 500,
      }}
    >
      {copied ? "Copied!" : "Copy link"}
    </button>
  );
}
