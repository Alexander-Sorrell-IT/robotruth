// Novus seam — Novus is the hackathon's analytics sponsor.
//
// RoboTruth's funnel runs fully WITHOUT Novus: every track() call already
// reaches our own /api/events sink (see ./analytics). Novus is a *second*
// forwarder layered on top, kept behind this one function so the rest of the
// app never imports the Novus SDK.
//
// To slot Novus in once access is granted — no other file changes:
//   1. Set NEXT_PUBLIC_NOVUS_SITE_ID in the env (.env.local locally, or the
//      Vercel project env). Its absence is what keeps this a no-op today.
//   2. Add the Novus snippet/SDK (e.g. a <Script> in app/layout.tsx) and
//      replace the TODO below with the real call.

import type { FunnelEvent, EventProps } from "./analytics";

const SITE_ID = process.env.NEXT_PUBLIC_NOVUS_SITE_ID;

// Novus runs on the Pendo agent: the layout.tsx snippet installs window.pendo
// (a queuing stub until the real agent loads), exposing pendo.track().
// The Window.pendo type is declared once, canonically, in pendo.d.ts.

export function forwardToNovus(event: FunnelEvent, props: EventProps): void {
  if (!SITE_ID) return; // disabled until access lands — no-op

  if (process.env.NODE_ENV !== "production") {
    console.debug("[novus:forward]", SITE_ID, event, props);
  }

  // Forward to the Pendo agent. The stub queues calls made before the agent
  // finishes loading, so this is safe to fire at any time.
  try {
    // EventProps allows null values; the Pendo agent tolerates them at runtime.
    window.pendo?.track?.(event, props as Record<string, string | number | boolean>);
  } catch {
    // analytics must never break the app
  }
}
