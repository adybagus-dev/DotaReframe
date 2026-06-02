"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, ArrowRight, ClipboardList, Loader2, Search } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { ButtonLink, StatusPill } from "@/components/ui";
import { savedReports } from "@/lib/sample-data";

export default function MatchPage() {
  const router = useRouter();
  const [matchId, setMatchId] = useState("8123456789");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const validation = useMemo(() => {
    if (!submitted && matchId.trim().length === 0) return "";
    if (!/^\d{7,12}$/.test(matchId.trim())) return "Use numbers only, for example 8123456789.";
    return "";
  }, [matchId, submitted]);

  function analyzeMatch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
    if (validation || !matchId.trim()) return;
    setLoading(true);
    window.setTimeout(() => {
      router.push(`/match/${matchId.trim()}/players`);
    }, 450);
  }

  return (
    <AppShell active="new-review">
      <div className="page-stack">
        <div className="page-heading">
          <span className="eyebrow">New Review</span>
          <h1>Analyze a Dota 2 Match</h1>
          <p>Paste a match ID, choose your hero, and get a coaching report written in simple language.</p>
        </div>

        <section className="input-panel">
          <div className="input-copy">
            <ClipboardList size={34} aria-hidden />
            <h2>Paste your Dota 2 match ID</h2>
            <p>You can find the match ID in your Dota 2 match history or on OpenDota.</p>
          </div>

          <form className="match-form" onSubmit={analyzeMatch}>
            <label htmlFor="match-id">Match ID</label>
            <div className="field-row">
              <Search size={18} aria-hidden />
              <input
                id="match-id"
                inputMode="numeric"
                pattern="[0-9]*"
                placeholder="8123456789"
                value={matchId}
                onChange={(event) => setMatchId(event.target.value)}
              />
            </div>
            {validation ? (
              <p className="field-error">
                <AlertCircle size={16} aria-hidden />
                {validation}
              </p>
            ) : null}
            <button className="button primary" disabled={loading || !matchId.trim()} type="submit">
              {loading ? <Loader2 size={18} aria-hidden className="spin" /> : <ArrowRight size={18} aria-hidden />}
              {loading ? "Fetching match data..." : "Analyze Match"}
            </button>
          </form>
        </section>

        <section className="state-grid" aria-label="Screen states">
          <article className="state-card">
            <StatusPill tone="info">Empty input</StatusPill>
            <p>Analyze Match stays disabled until the user enters a match ID.</p>
          </article>
          <article className="state-card">
            <StatusPill tone="risk">OpenDota error</StatusPill>
            <p>Show a clear retry message without blaming the user.</p>
          </article>
          <article className="state-card">
            <StatusPill tone="good">Match found</StatusPill>
            <p>Move the user to the player selection screen.</p>
          </article>
        </section>

        {savedReports.length ? (
          <section className="recent-card">
            <div>
              <span>Recent saved report</span>
              <h2>{savedReports[0].hero}</h2>
              <p>{savedReports[0].main_problem}</p>
            </div>
            <ButtonLink href={`/reports/${savedReports[0].id}`} variant="secondary">
              Open Report
            </ButtonLink>
          </section>
        ) : null}
      </div>
    </AppShell>
  );
}
