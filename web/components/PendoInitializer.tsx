"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    pendo?: {
      initialize: (opts: { visitor: Record<string, unknown> }) => void;
      identify: (opts: { visitor: Record<string, unknown> }) => void;
      track?: (event: string, props?: Record<string, unknown>) => void;
    };
  }
}

function getOrCreateVisitorId(): string {
  try {
    const key = "rt_vid";
    let id = localStorage.getItem(key);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(key, id);
    }
    return id;
  } catch {
    return "anonymous";
  }
}

/** Call after meaningful user actions to update visitor metadata in Novus. */
export function enrichPendoVisitor(props: Record<string, unknown>): void {
  try {
    window.pendo?.identify?.({
      visitor: { id: localStorage.getItem("rt_vid") ?? "anonymous", ...props },
    });
  } catch {
    // analytics must never break the app
  }
}

export function PendoInitializer() {
  useEffect(() => {
    if (typeof window === "undefined" || !window.pendo) return;
    window.pendo.initialize({
      visitor: {
        id: getOrCreateVisitorId(),
        referrer: document.referrer || "direct",
        landingPage: window.location.pathname,
      },
    });
  }, []);

  return null;
}
