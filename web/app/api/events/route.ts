import { EVENTS } from "@/lib/analytics";

const EVENT_SET = new Set<string>(EVENTS);

// Funnel sink. Validates the event against the §12 set and emits one
// structured log line per accepted event — the serverless logs are the
// working dashboard substitute until Novus is connected.
export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return new Response("bad json", { status: 400 });
  }

  const { event, props, ts, path } = (body ?? {}) as Record<string, unknown>;
  if (typeof event !== "string" || !EVENT_SET.has(event)) {
    return new Response("unknown event", { status: 400 });
  }

  console.log(
    JSON.stringify({
      at: "funnel",
      event,
      props: props ?? {},
      ts: typeof ts === "number" ? ts : Date.now(),
      path: typeof path === "string" ? path : null,
    }),
  );

  return new Response(null, { status: 204 });
}
