"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  Clock3,
  Gamepad2,
  Loader2,
  LogOut,
  Search
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { StatusPill } from "@/components/ui";
import type { RecentMatch } from "@/lib/types";

const ACCOUNT_KEY = "dotareframe.steam-account.v1";

export default function MatchPage() {
  const router = useRouter();
  const [matchId, setMatchId] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [accountId, setAccountId] = useState("");
  const [recentMatches, setRecentMatches] = useState<RecentMatch[]>([]);
  const [recentLoading, setRecentLoading] = useState(false);
  const [recentError, setRecentError] = useState("");

  const validation = useMemo(() => {
    if (!submitted && matchId.trim().length === 0) return "";
    if (!/^\d{7,12}$/.test(matchId.trim())) return "Use numbers only, for example 8123456789.";
    return "";
  }, [matchId, submitted]);

  useEffect(() => {
    const connected = new URLSearchParams(window.location.search).get("steam_account_id");
    const stored = window.localStorage.getItem(ACCOUNT_KEY);
    const nextAccount = connected ?? stored ?? "";
    if (connected) {
      window.localStorage.setItem(ACCOUNT_KEY, connected);
      window.history.replaceState({}, "", "/match");
    }
    setAccountId(nextAccount);
  }, []);

  useEffect(() => {
    if (!accountId) return;
    let cancelled = false;
    setRecentLoading(true);
    setRecentError("");
    fetch(`/api/recent-matches/${accountId}`, { cache: "no-store" })
      .then(async (response) => {
        const payload = (await response.json()) as { matches?: RecentMatch[]; detail?: string };
        if (!response.ok) throw new Error(payload.detail ?? "Recent matches could not be loaded.");
        if (!cancelled) setRecentMatches(payload.matches ?? []);
      })
      .catch((error: Error) => {
        if (!cancelled) setRecentError(error.message);
      })
      .finally(() => {
        if (!cancelled) setRecentLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [accountId]);

  function analyzeMatch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
    if (validation || !matchId.trim()) return;
    setLoading(true);
    router.push(`/match/${matchId.trim()}/players${accountId ? `?accountId=${accountId}` : ""}`);
  }

  function disconnectSteam() {
    window.localStorage.removeItem(ACCOUNT_KEY);
    setAccountId("");
    setRecentMatches([]);
    setRecentError("");
  }

  return (
    <AppShell active="new-review">
      <div className="page-stack">
        <div className="page-heading">
          <span className="eyebrow">New Review</span>
          <h1>Turn your last match into one clear fix</h1>
          <p>Choose a recent public match or paste its ID. DotaReframe will judge your stats by the role you actually played.</p>
        </div>

        <section className="steam-panel">
          <div>
            <Gamepad2 size={28} aria-hidden />
            <div>
              <h2>{accountId ? "Steam connected" : "Find your recent matches"}</h2>
              <p>
                {accountId
                  ? "Your latest public Dota 2 matches are ready below."
                  : "Connect Steam once so you do not need to copy a match ID every time."}
              </p>
            </div>
          </div>
          {accountId ? (
            <button className="button secondary" type="button" onClick={disconnectSteam}>
              <LogOut size={17} aria-hidden />
              Disconnect
            </button>
          ) : (
            <a className="button steam-button" href="/api/steam/login">
              <Gamepad2 size={18} aria-hidden />
              Connect Steam
            </a>
          )}
        </section>

        {accountId ? (
          <section className="section-block">
            <div className="section-heading">
              <span>Recent public matches</span>
              <h2>Pick the game you want to improve from</h2>
            </div>
            {recentLoading ? (
              <div className="loading-message">
                <Loader2 size={20} className="spin" aria-hidden />
                <div>
                  <strong>Loading recent matches</strong>
                  <span>Checking OpenDota for your latest public games.</span>
                </div>
              </div>
            ) : recentError ? (
              <div className="inline-error">
                <AlertCircle size={18} aria-hidden />
                <span>{recentError}</span>
              </div>
            ) : recentMatches.length ? (
              <div className="recent-match-list">
                {recentMatches.map((match) => (
                  <Link
                    className="recent-match-row"
                    href={`/match/${match.match_id}/players?accountId=${accountId}`}
                    key={match.match_id}
                  >
                    <div className="hero-avatar info">{match.hero.slice(0, 1)}</div>
                    <div>
                      <strong>{match.hero}</strong>
                      <span>
                        Match {match.match_id} · {match.kda}
                      </span>
                    </div>
                    <div className="recent-match-meta">
                      <StatusPill tone={match.result === "Won" ? "good" : "risk"}>{match.result}</StatusPill>
                      <span>
                        <Clock3 size={14} aria-hidden />
                        {match.duration_minutes}m
                      </span>
                      <ArrowRight size={18} aria-hidden />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="inline-note">
                <CheckCircle2 size={18} aria-hidden />
                No public recent matches were found. You can still paste a match ID below.
              </div>
            )}
          </section>
        ) : null}

        <section className="input-panel">
          <div className="input-copy">
            <ClipboardList size={34} aria-hidden />
            <h2>Or paste a Dota 2 match ID</h2>
            <p>Open Dota 2, choose Watch, then Match History. The match ID appears in the match details.</p>
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
            <button className="button primary" disabled={loading || !matchId.trim() || Boolean(validation)} type="submit">
              {loading ? <Loader2 size={18} aria-hidden className="spin" /> : <ArrowRight size={18} aria-hidden />}
              {loading ? "Opening match..." : "Choose My Hero"}
            </button>
          </form>
        </section>
      </div>
    </AppShell>
  );
}
