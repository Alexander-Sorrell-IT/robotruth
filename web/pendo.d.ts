interface Pendo {
  track(event: string, properties?: Record<string, string | number | boolean>): void;
}

interface Window {
  pendo?: Pendo;
}
