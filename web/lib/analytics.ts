import { forwardToNovus } from "./novus";

// The §12 funnel. This is the single definition of the event set — the
// /api/events sink validates against EVENTS, so adding an event here is all
// it takes to make it accepted end-to-end.
export const EVENTS = [
  "landing_view",
  "pr_pasted",
  "example_clicked",
  "receipt_generated", // activation event
  "receipt_viewed",    // shared receipt opened by any visitor
  "receipt_shared",
  "image_copied",
  "wall_view",
  "bots_view",
  "insights_view",
  "badge_view",
  "github_action_view",
  "repo_scorecard_view",
  "submitted_to_wall",
] as const;

export type FunnelEvent = (typeof EVENTS)[number];
export type EventProps = Record<string, string | number | boolean | null>;

// Fire a funnel event. Safe to call anywhere; never throws, never blocks.
// Works fully without Novus — events go to our own /api/events sink. Novus,
// when connected, is an additional forwarder (see ./novus).
export function track(event: FunnelEvent, props: EventProps = {}): void {
  if (typeof window === "undefined") return; // client-only

  if (process.env.NODE_ENV !== "production") {
    console.debug("[analytics]", event, props);
  }

  // Working local sink: a fire-and-forget beacon to our own route handler,
  // which validates + logs. This is the analytics you have without Novus.
  try {
    const body = JSON.stringify({ event, props, ts: Date.now(), path: window.location.pathname });
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/api/events", new Blob([body], { type: "application/json" }));
    } else {
      fetch("/api/events", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body,
        keepalive: true,
      });
    }
  } catch {
    // analytics must never break the app
  }

  // The Novus seam — no-op until NEXT_PUBLIC_NOVUS_SITE_ID is set.
  forwardToNovus(event, props);
}
