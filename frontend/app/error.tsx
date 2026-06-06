"use client";

import { AlertCircle, RotateCcw } from "lucide-react";

export default function ErrorPage({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="fatal-error">
      <AlertCircle size={30} aria-hidden />
      <h1>We could not load this Dota data</h1>
      <p>{error.message || "The request failed. Please try again."}</p>
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
