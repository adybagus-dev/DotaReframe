import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Flame,
  Gamepad2,
  Target,
  TrendingUp
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { MatchIdForm } from "@/components/match-id-form";
import { StatusPill } from "@/components/ui";
import { getDashboard, getMyRecentMatches } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MatchPage() {
  const dashboard = await getDashboard();
  const connected = Boolean(dashboard.profile.steam_account_id);
  const recentMatches = connected ? await getMyRecentMatches() : [];
  const latestMatch = recentMatches[0];

  return (
    <AppShell active="new-review">
      <div className="page-stack">
        <div className="page-heading split">
          <div>
            <span className="eyebrow">{dashboard.total_reports ? "Welcome Back" : "New Review"}</span>
            <h1>{dashboard.total_reports ? "Keep improving one match at a time" : "Turn your last match into one clear fix"}</h1>
            <p>
              {dashboard.total_reports
                ? "Your mission stays here between matches, so the next review can show whether the habit improved."
                : "Review one public match, leave with one measurable mission, then come back after your next game."}
            </p>
          </div>
          {connected ? (
            <form action="/api/session/logout" method="post">
              <button className="button secondary" type="submit">Disconnect Steam</button>
            </form>
          ) : (
            <a className="button steam-button" href="/api/steam/login">
              <Gamepad2 size={18} aria-hidden />
              Connect Steam
            </a>
          )}
        </div>

        <section className="progress-hero">
          <div className="progress-primary">
            <span><Target size={18} aria-hidden /> Current mission</span>
            <h2>{dashboard.active_mission?.title ?? "Complete your first review"}</h2>
            <p>
              {dashboard.active_mission?.explanation ??
                "DotaReframe will turn your match into one goal that is easy to check after the next game."}
            </p>
            {latestMatch ? (
              <Link className="button primary" href={`/match/${latestMatch.match_id}/review`}>
                Review Latest Match
                <ArrowRight size={18} aria-hidden />
              </Link>
            ) : (
              <a className="button primary" href="#manual-review">Start First Review</a>
            )}
          </div>
          <div className="progress-stats">
            <article>
              <Flame size={20} aria-hidden />
              <strong>{dashboard.mission_streak}</strong>
              <span>mission streak</span>
            </article>
            <article>
              <TrendingUp size={20} aria-hidden />
              <strong>{dashboard.total_reports}</strong>
              <span>matches reviewed</span>
            </article>
            <article>
              <CheckCircle2 size={20} aria-hidden />
              <strong>{dashboard.latest_progress?.completed ? "Improved" : dashboard.latest_progress ? "In progress" : "Ready"}</strong>
              <span>latest mission</span>
            </article>
          </div>
        </section>

        {connected ? (
          <section className="section-block">
            <div className="section-heading">
              <span>Recent public matches</span>
              <h2>Choose the next match to learn from</h2>
            </div>
            {recentMatches.length ? (
              <div className="recent-match-list">
                {recentMatches.slice(0, 6).map((match) => (
                  <Link className="recent-match-row" href={`/match/${match.match_id}/review`} key={match.match_id}>
                    <div className="hero-avatar info">{match.hero.slice(0, 1)}</div>
                    <div>
                      <strong>{match.hero}</strong>
                      <span>Match {match.match_id} · {match.kda}</span>
                    </div>
                    <div className="recent-match-meta">
                      <StatusPill tone={match.result === "Won" ? "good" : "risk"}>{match.result}</StatusPill>
                      <span><Clock3 size={14} aria-hidden />{match.duration_minutes}m</span>
                      <ArrowRight size={18} aria-hidden />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="inline-note">No public recent matches were found. You can still paste a match ID below.</div>
            )}
          </section>
        ) : (
          <section className="steam-panel">
            <div>
              <Gamepad2 size={28} aria-hidden />
              <div>
                <h2>Keep progress across devices</h2>
                <p>Connect Steam after your first review to restore your mission and private history anywhere.</p>
              </div>
            </div>
            <a className="button steam-button" href="/api/steam/login">Connect Steam</a>
          </section>
        )}

        <MatchIdForm connected={connected} />

        {dashboard.recent_reports.length ? (
          <section className="section-block">
            <div className="section-heading">
              <span>Your history</span>
              <h2>Recent coaching reports</h2>
            </div>
            <div className="mini-report-grid">
              {dashboard.recent_reports.map((report) => (
                <Link href={`/reports/${report.id}`} className="mini-report" key={report.id}>
                  <strong>{report.hero}</strong>
                  <span>{report.result} · {report.kda}</span>
                  <p>{report.main_problem}</p>
                </Link>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </AppShell>
  );
}
