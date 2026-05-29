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

export function forwardToNovus(event: FunnelEvent, props: EventProps): void {
  if (!SITE_ID) return; // disabled until access lands — no-op

  // TODO(novus): forward to the real Novus SDK once we have access, e.g.
  //   window.novus?.track(event, props);
  // The SDK shape isn't known yet, so for now we log to prove the wiring is
  // live end-to-end the moment SITE_ID is set.
  if (process.env.NODE_ENV !== "production") {
    console.debug("[novus:forward]", SITE_ID, event, props);
  }
}
