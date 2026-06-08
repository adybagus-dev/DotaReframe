"use client";

import { useEffect, useState } from "react";
import { BUILD_ID, BUILD_ID_STORAGE_KEY, BUILD_RELOAD_KEY, STALE_RELOAD_KEY } from "@/lib/build";

type BuildInfoResponse = {
  buildId?: string;
};

async function clearAppCaches() {
  try {
    if (!("caches" in window)) {
      return;
    }
    const keys = await window.caches.keys();
    await Promise.all(keys.map((key) => window.caches.delete(key)));
  } catch {
    // Best effort only. Stale cache cleanup should never block the app.
  }
}

export function DeployGuard() {
  const [staleBundle, setStaleBundle] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function checkBuild() {
      try {
        const response = await fetch("/api/build-info", { cache: "no-store" });
        if (!response.ok) {
          return;
        }
        const payload = (await response.json()) as BuildInfoResponse;
        const liveBuildId = payload.buildId?.trim();
        if (!liveBuildId) {
          return;
        }

        window.localStorage.setItem(BUILD_ID_STORAGE_KEY, liveBuildId);

        if (liveBuildId !== BUILD_ID) {
          const reloadMarker = window.sessionStorage.getItem(BUILD_RELOAD_KEY);
          if (reloadMarker === liveBuildId) {
            setStaleBundle(true);
            return;
          }

          window.sessionStorage.setItem(BUILD_RELOAD_KEY, liveBuildId);
          await clearAppCaches();
          if (!cancelled) {
            window.location.reload();
          }
          return;
        }

        window.sessionStorage.removeItem(BUILD_RELOAD_KEY);
        window.sessionStorage.removeItem(STALE_RELOAD_KEY);
      } catch {
        // If the version probe is unavailable, fail open.
      }
    }

    void checkBuild();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const handler = (event: Event) => {
      const errorEvent = event as ErrorEvent;
      const message = String(errorEvent.error?.message ?? errorEvent.message ?? "");
      if (!/ChunkLoadError|Loading chunk|Cannot find module|failed to fetch dynamically imported module|Importing a module script failed/i.test(message)) {
        return;
      }

      const marker = window.sessionStorage.getItem(BUILD_RELOAD_KEY);
      if (marker === "chunk-error") {
        setStaleBundle(true);
        return;
      }

      window.sessionStorage.setItem(BUILD_RELOAD_KEY, "chunk-error");
      void clearAppCaches().finally(() => window.location.reload());
    };

    window.addEventListener("error", handler);
    return () => window.removeEventListener("error", handler);
  }, []);

  useEffect(() => {
    if (!staleBundle) {
      return;
    }
    window.sessionStorage.removeItem(BUILD_RELOAD_KEY);
  }, [staleBundle]);

  return null;
}
