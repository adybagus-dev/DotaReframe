"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Loader2, RotateCcw } from "lucide-react";
import { ReportView } from "@/components/report-view";
import type { CoachingReport } from "@/lib/types";

type ReportLoaderProps = {
  matchId: string;
  playerSlot: string;
  role?: string;
  accountId?: string;
};

export function ReportLoader({ matchId, playerSlot, role, accountId }: ReportLoaderProps) {
  const [report, setReport] = useState<CoachingReport | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadReport() {
      setError("");
      setReport(null);

      try {
        const response = await fetch("/api/me/reports", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            match_id: Number(matchId),
            player_slot: Number(playerSlot),
            role,
            account_id: accountId ? Number(accountId) : undefined
          })
        });

        if (!response.ok) {
          const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
          throw new Error(payload?.detail ?? "The report could not be generated. Please try again.");
        }

        const payload = (await response.json()) as CoachingReport;
        if (active) setReport(payload);
      } catch (requestError) {
        if (!active) return;
        setError(
          requestError instanceof Error
            ? requestError.message
            : "DotaReframe could not reach the coaching server. Please try again."
        );
      }
    }

    void loadReport();
    return () => {
      active = false;
    };
  }, [accountId, attempt, matchId, playerSlot, role]);

  if (report) return <ReportView report={report} />;

  if (error) {
    return (
      <section className="report-load-state error-state" role="alert">
        <AlertCircle size={30} aria-hidden />
        <span className="eyebrow">Report interrupted</span>
        <h1>We could not finish this review</h1>
        <p>{error}</p>
        <div className="report-load-actions">
          <button className="button primary" type="button" onClick={() => setAttempt((value) => value + 1)}>
            <RotateCcw size={18} aria-hidden />
            Try Again
          </button>
          <a className="button secondary" href="/match">Choose Another Match</a>
        </div>
      </section>
    );
  }

  return (
    <section className="report-load-state" aria-live="polite">
      <Loader2 size={34} className="spin" aria-hidden />
      <span className="eyebrow">Analyzing match {matchId}</span>
      <h1>Building your coaching report</h1>
      <p>
        Checking saved reports first, then reading the public match only if DotaReframe needs a fresh review.
        A brand-new match can still take up to a minute.
      </p>
      <div className="report-load-steps" aria-hidden>
        <span className="is-active">Checking saved report</span>
        <span>Reading match data</span>
        <span>Building role review</span>
        <span>Saving report</span>
      </div>
    </section>
  );
}
