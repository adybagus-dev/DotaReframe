import Link from "next/link";
import {
  ArrowRight,
  Clock3,
  Gamepad2,
  Target,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { MatchIdForm } from "@/components/match-id-form";
import { ButtonLink, EmptyState, StatusPill } from "@/components/ui";
import { getDashboard, getMyRecentMatches } from "@/lib/api";
import type { DashboardSummary } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function MatchPage() {
  let dashboard: DashboardSummary | null = null;
  try {
    dashboard = await getDashboard();
  } catch {
    return (
      <AppShell active="new-review">
        <div className="page-stack">
          <div className="page-heading">
            <span className="eyebrow">New Review</span>
            <h1>Review newest match</h1>
            <p>We could not load your dashboard right now, but your saved reports are still safe.</p>
          </div>
          <EmptyState
            title="Dashboard temporarily unavailable"
            body="Try again in a moment. If this keeps happening, start a manual review from a match ID."
            action={<ButtonLink href="/match">Try Again</ButtonLink>}
          />
          <div id="manual-review">
            <MatchIdForm connected={false} />
          </div>
        </div>
      </AppShell>
    );
  }

  const connected = Boolean(dashboard?.profile?.steam_account_id);
  const recentMatches = connected ? await getMyRecentMatches().catch(() => []) : [];
  const latestMatch = recentMatches[0];
  const latestReviewedReport = dashboard?.recent_reports?.[0];

  return (
    <AppShell active="new-review">
      <div className="page-stack">
        <div className="page-heading split">
          <div>
            <span className="eyebrow">{connected ? "Review newest match" : "New Review"}</span>
            <h1>Review newest match</h1>
            <p>
              {connected
                ? "This is the most recent public match from OpenDota."
                : "Review one public match and get one clear mission to bring into the next game."}
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

        <section className="review-now-card">
          <div className="review-now-icon">
            <Gamepad2 size={24} aria-hidden />
          </div>
          <div>
            <span>Newest public match</span>
            {latestMatch ? (
              <>
                <h2>{latestMatch.hero}</h2>
                <p>Match {latestMatch.match_id} · {latestMatch.result} · {latestMatch.kda} · {latestMatch.duration_minutes}m</p>
                <small>This is the most recent match from OpenDota. Review it to update your mission.</small>
              </>
            ) : (
              <>
                <h2>No newest match found</h2>
                <p>Connect Steam or paste a match ID to start reviewing.</p>
                <small>Your next mission will update after a saved review.</small>
              </>
            )}
          </div>
          {latestMatch ? (
            <Link className="button primary" href={`/match/${latestMatch.match_id}/review`}>
              Review Latest Match
              <ArrowRight size={18} aria-hidden />
            </Link>
          ) : (
            <a className="button primary" href="#manual-review">
              Start First Review
            </a>
          )}
        </section>

        <section className="mission-card">
          <div className="mission-icon">
            <Target size={24} aria-hidden />
          </div>
          <div>
            <span>Mission from last review</span>
            <h2>{dashboard?.active_mission?.title ?? "Complete your first review"}</h2>
            <p>
              {dashboard?.active_mission?.explanation ??
                "DotaReframe will turn your match into one goal that is easy to check after the next game."}
            </p>
            <strong>
              {latestReviewedReport ? `Based on your last reviewed match, Match ${latestReviewedReport.match_id}.` : "Save one review to create your first mission."}
            </strong>
          </div>
        </section>

        <div id="manual-review">
          <MatchIdForm connected={connected} />
        </div>

        {connected ? (
          <section className="section-block">
            <div className="section-heading">
              <span>Recent public matches</span>
              <h2>Open an older match</h2>
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
        ) : null}

        {dashboard?.recent_reports?.length ? (
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
