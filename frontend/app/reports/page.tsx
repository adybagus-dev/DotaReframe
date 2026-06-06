import Link from "next/link";
import { CalendarDays, ChevronRight } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { ButtonLink, EmptyState, StatusPill } from "@/components/ui";
import { getSavedReports } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ReportsPage() {
  const reports = await getSavedReports();

  return (
    <AppShell active="saved-reports">
      <div className="page-stack">
        <div className="page-heading split">
          <div>
            <span className="eyebrow">Saved Reports</span>
            <h1>Saved Match Reviews</h1>
            <p>Reopen your coaching history and check whether the same problem keeps appearing.</p>
          </div>
          <ButtonLink href="/match" variant="secondary">
            Analyze Another Match
          </ButtonLink>
        </div>

        {reports.length === 0 ? (
          <EmptyState
            title="No saved reports yet"
            body="Analyze a match first, then your reports will appear here."
            action={<ButtonLink href="/match">Start New Review</ButtonLink>}
          />
        ) : (
          <section className="saved-list">
            {reports.map((report) => (
              <Link className="saved-card" href={`/reports/${report.id}`} key={report.id}>
                <div className="saved-hero">
                  <div className="hero-avatar info">{report.hero.slice(0, 1)}</div>
                  <div>
                    <h2>{report.hero}</h2>
                    <p>
                      Match: {report.match_id} · {report.result}
                    </p>
                  </div>
                </div>
                <div className="saved-stats">
                  <span>KDA: {report.kda}</span>
                  <span>GPM: {report.gpm}</span>
                </div>
                <p className="saved-problem">Main thing to fix: {report.main_problem}</p>
                <div className="saved-footer">
                  <span>
                    <CalendarDays size={16} aria-hidden />
                    {report.created_at}
                  </span>
                  <StatusPill tone={report.confidence === "high" ? "good" : "neutral"}>
                    Confidence: {report.confidence}
                  </StatusPill>
                  <span className="open-report">
                    Open Report
                    <ChevronRight size={16} aria-hidden />
                  </span>
                </div>
              </Link>
            ))}
          </section>
        )}
      </div>
    </AppShell>
  );
}
