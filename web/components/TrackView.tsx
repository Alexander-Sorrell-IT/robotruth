"use client";
import { useEffect } from "react";
import { track, type FunnelEvent, type EventProps } from "@/lib/analytics";

// Fires one funnel event on mount. Drop into a server component to record a
// view (e.g. <TrackView event="wall_view" />). Props must be serializable.
export function TrackView({ event, props }: { event: FunnelEvent; props?: EventProps }) {
  useEffect(() => {
    track(event, props);
    // mount-only; the event/props for a given mounted page don't change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return null;
}
