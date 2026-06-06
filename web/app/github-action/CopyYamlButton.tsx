"use client";
import { useState } from "react";

export function CopyYamlButton({ yaml }: { yaml: string }) {
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard
      ?.writeText(yaml)
      .then(() => {
        if (typeof window !== "undefined" && window.pendo) {
          window.pendo.track("github_action_yaml_copied", {
            yamlLength: yaml.length,
          });
        }
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(() => {});
  }

  return (
    <button
      onClick={copy}
      style={{
        padding: "7px 16px",
        borderRadius: 8,
        border: "1px solid #e5e7eb",
        background: "#fff",
        color: "#374151",
        fontSize: 13,
        fontWeight: 600,
        cursor: "pointer",
      }}
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}
