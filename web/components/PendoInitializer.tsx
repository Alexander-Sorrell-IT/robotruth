"use client";

import { useEffect } from "react";

export function PendoInitializer() {
  useEffect(() => {
    if (typeof window !== "undefined" && window.pendo) {
      pendo.initialize({
        visitor: {
          id: "",
        },
      });
    }
  }, []);

  return null;
}
