"use client";

import { useEffect, useMemo } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { STALE_RELOAD_KEY } from "@/lib/build";

export default function ErrorPage({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const staleBundle = useMemo(() => {
    const message = String(error?.message ?? "");
    return /ChunkLoadError|Loading chunk|Cannot find module|failed to fetch dynamically imported module|Importing a module script failed/i.test(
      message
    );
  }, [error]);

  useEffect(() => {
    if (!staleBundle || typeof window === "undefined") {
      return;
    }

    const tried = window.sessionStorage.getItem(STALE_RELOAD_KEY);
    if (tried === "1") {
      return;
    }

    window.sessionStorage.setItem(STALE_RELOAD_KEY, "1");
    window.location.reload();
  }, [staleBundle]);

  const title = staleBundle ? "This copy of DotaReframe is out of date" : "We could not load this Dota data";
  const description = staleBundle
    ? "Your browser likely held an older app bundle. We tried one automatic refresh. If this page still stays stuck, hard refresh once."
    : error.message || "The request failed. Please try again.";

  return (
    <main className="fatal-error">
      <AlertCircle size={30} aria-hidden />
      <h1>{title}</h1>
      <p>{description}</p>
      <button className="button primary" type="button" onClick={reset}>
        <RotateCcw size={18} aria-hidden />
        Try Again
      </button>
      <a className="text-link" href="/match">
        Return to New Review
      </a>
    </main>
  );
}
