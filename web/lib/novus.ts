// Novus seam — Novus is the hackathon's analytics sponsor.
//
// RoboTruth's funnel runs fully WITHOUT Novus: every track() call already
// reaches our own /api/events sink (see ./analytics). Novus is a *second*
// forwarder layered on top, kept behind this one function so the rest of the
// app never imports the Novus SDK.
//
// Novus is active once its Pendo agent is installed (a <Script> in
// app/layout.tsx, which exposes window.pendo). The forwarder below fires
// whenever that agent is present — no env var required (see the NOTE below).

import type { FunnelEvent, EventProps } from "./analytics";

// Novus runs on the Pendo agent, installed unconditionally by the layout.tsx
// snippet. We forward the §12 funnel whenever that agent is present on the page.
// The Window.pendo type is declared once, canonically, in pendo.d.ts.
//
// NOTE: this does NOT gate on NEXT_PUBLIC_NOVUS_SITE_ID. This (non-standard) Next
// build does not inline NEXT_PUBLIC_* into the client bundle, so an env gate would
// read undefined in the browser and never fire. The agent's runtime presence
// (window.pendo) is the correct, reliable gate instead.

export function forwardToNovus(event: FunnelEvent, props: EventProps): void {
  if (typeof window === "undefined") return; // client-only

  // Forward to the Pendo agent. The stub queues calls made before the agent
  // finishes loading, so this is safe to fire at any time.
  try {
    // EventProps allows null values; the Pendo agent tolerates them at runtime.
    window.pendo?.track?.(event, props as Record<string, string | number | boolean>);
  } catch {
    // analytics must never break the app
  }
}
