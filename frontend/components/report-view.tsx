import Link from "next/link";
import { ArrowLeft, Archive, CheckCircle2, ChevronDown, ListChecks, RotateCcw, Target } from "lucide-react";
import type { CoachingReport, SnapshotValue } from "@/lib/types";
import { ButtonLink, StatusPill } from "./ui";

function snapshotTone(value: SnapshotValue) {
  if (value === "Good") return "good";
  if (value === "Needs Work") return "risk";
  if (value === "Low Impact") return "warning";
  return "info";
}

export function ReportView({
  report,
  savedDetail = false
}: {
  report: CoachingReport;
  savedDetail?: boolean;
}) {
  const snapshot = Object.entries(report.performance_snapshot);
  const timingNotes = report.timing_notes ?? [];
  const decisionRules = report.decision_rules ?? [];
  const checklist = report.next_game_checklist ?? [];
  const practiceDrills = report.practice_drills ?? [];
  const primaryMistake = report.mistakes[0];

  return (
    <div className="page-stack">
      <div className="page-heading split">
        <div>
          <span className="eyebrow">{savedDetail ? `Saved report / ${report.created_at}` : "Review Report"}</span>
          <h1>{report.hero} Review</h1>
          <p>
            You played {report.hero}. Here is the clearest thing to fix and what to practice next.
          </p>
        </div>
        <div className="heading-actions">
          <StatusPill tone="good">Saved locally</StatusPill>
          <ButtonLink href="/match" variant="secondary" icon={RotateCcw}>
            Analyze Another Match
          </ButtonLink>
        </div>
      </div>

      <section className="summary-grid" aria-label="Match summary">
        <MetricCard label="Result" value={report.result} />
        <MetricCard label="Duration" value={`${report.summary.duration_minutes}m`} />
        <MetricCard label="KDA" value={report.summary.kda} />
        <MetricCard label="GPM" value={String(report.summary.gpm)} />
        <MetricCard label="XPM" value={String(report.summary.xpm)} />
        <MetricCard label="Last Hits" value={String(report.summary.last_hits)} />
        <MetricCard label="Deaths" value={String(report.summary.deaths)} />
      </section>

      <section className="focus-card">
        <div>
          <span>Main thing to fix</span>
          <h2>{report.main_problem}</h2>
          <p>
            Evidence: {report.main_evidence.join(", ")}. Try next game:{" "}
            {primaryMistake?.try_next_game ?? "focus on one clear habit you can repeat for the next match."}
          </p>
        </div>
      </section>

      {report.match_story ? (
        <section className="coach-story">
          <span>What happened in plain language</span>
          <p>{report.match_story}</p>
        </section>
      ) : null}

      <section className="performance-grid" aria-label="Performance snapshot">
        {snapshot.map(([name, value]) => (
          <article className={`performance-card ${snapshotTone(value)}`} key={name}>
            <span>{name}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="section-block">
        <div className="section-heading">
          <span>Top 3 Mistakes</span>
          <h2>What to clean up next game</h2>
        </div>
        <div className="mistake-grid">
          {report.mistakes.map((mistake) => (
            <article className="mistake-card" key={mistake.title}>
              <h3>{mistake.title}</h3>
              <p>{mistake.what_happened}</p>
              <div className="evidence-box">
                <strong>Evidence</strong>
                <ul>
                  {mistake.evidence.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <p>
                <strong>Why it matters:</strong> {mistake.why_it_matters}
              </p>
              <p>
                <strong>Try next game:</strong> {mistake.try_next_game}
              </p>
            </article>
          ))}
        </div>
      </section>

      {timingNotes.length ? (
        <section className="section-block">
          <div className="section-heading">
            <span>Timing Notes</span>
            <h2>When the game started to get hard</h2>
          </div>
          <div className="timing-grid">
            {timingNotes.map((note) => (
              <article className="timing-card" key={note.phase}>
                <strong>{note.phase}</strong>
                <p>{note.what_to_notice}</p>
                <div>
                  <Target size={16} aria-hidden />
                  <span>{note.do_next_game}</span>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {decisionRules.length || checklist.length ? (
        <div className="two-column">
          {decisionRules.length ? (
            <section className="plain-card action-card">
              <span>
                <ListChecks size={16} aria-hidden />
                Decision rules
              </span>
              <ul className="clean-list">
                {decisionRules.map((rule) => (
                  <li key={rule}>{rule}</li>
                ))}
              </ul>
            </section>
          ) : null}
          {checklist.length ? (
            <section className="plain-card action-card">
              <span>
                <CheckCircle2 size={16} aria-hidden />
                Next-game checklist
              </span>
              <ul className="clean-list">
                {checklist.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      ) : null}

      <div className="two-column">
        <section className="plain-card">
          <span>What you did well</span>
          <ul className="clean-list">
            {report.strengths.map((strength) => (
              <li key={strength}>{strength}</li>
            ))}
          </ul>
        </section>
        <section className="plain-card">
          <span>Next 3 games training plan</span>
          <ol className="clean-list ordered">
            {report.training_plan.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </section>
      </div>

      {practiceDrills.length ? (
        <section className="section-block">
          <div className="section-heading">
            <span>Practice Drills</span>
            <h2>How to improve this, not just read it</h2>
          </div>
          <div className="drill-grid">
            {practiceDrills.map((drill) => (
              <article className="drill-card" key={drill.title}>
                <h3>{drill.title}</h3>
                <p>
                  <strong>Goal:</strong> {drill.goal}
                </p>
                <p>
                  <strong>Practice:</strong> {drill.how_to_practice}
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <details className="evidence-panel">
        <summary>
          <span>Match evidence</span>
          <ChevronDown size={18} aria-hidden />
        </summary>
        <ul>
          {report.match_evidence.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </details>

      <section className="limitation-note">
        <strong>AI limitation note</strong>
        <p>{report.limitations.join(" ")}</p>
      </section>

      <div className="footer-actions">
        <Link href={`/match/${report.match_id}/players`} className="text-link">
          <ArrowLeft size={16} aria-hidden />
          Back to Players
        </Link>
        <ButtonLink href="/reports" variant="secondary" icon={Archive}>
          Open Saved Reports
        </ButtonLink>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
