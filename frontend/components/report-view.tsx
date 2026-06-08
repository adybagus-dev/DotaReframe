import Link from "next/link";
import {
  ArrowLeft,
  Archive,
  CheckCircle2,
  ChevronDown,
  CircleDot,
  ShieldAlert,
  ListChecks,
  RotateCcw,
  Target,
  TrendingUp
} from "lucide-react";
import type { CoachingReport, SnapshotValue } from "@/lib/types";
import { ButtonLink, StatusPill } from "./ui";
import { ReportFeedback } from "./report-feedback";

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
  const itemReview = report.item_timing_review;

  return (
    <div className="page-stack">
      <div className="page-heading split">
        <div>
          <span className="eyebrow">{savedDetail ? `Saved report / ${report.created_at}` : "Review Report"}</span>
          <h1>{report.hero} Review</h1>
          <p>
            You played {report.hero} as {report.role}. Here is the clearest thing to fix and what to practice next.
          </p>
        </div>
        <div className="heading-actions">
          <StatusPill tone="good">Saved to reports</StatusPill>
          <ButtonLink href="/match" variant="secondary" icon={RotateCcw}>
            Analyze Another Match
          </ButtonLink>
        </div>
      </div>

      <section className="summary-grid" aria-label="Match summary">
        <MetricCard label="Result" value={report.result} />
        <MetricCard label="Role" value={report.role} />
        <MetricCard label="Duration" value={`${report.summary.duration_minutes}m`} />
        <MetricCard label="KDA" value={report.summary.kda} />
      </section>

      {report.next_match_mission ? (
        <section className="mission-card">
          <div className="mission-icon">
            <Target size={24} aria-hidden />
          </div>
          <div>
            <span>Your next-match mission</span>
            <h2>{report.next_match_mission.title}</h2>
            <p>{report.next_match_mission.explanation}</p>
            <strong>{report.next_match_mission.check_text}</strong>
          </div>
        </section>
      ) : null}

      {report.progress ? (
        <section className={`progress-card ${report.progress.completed ? "complete" : "active"}`}>
          <TrendingUp size={22} aria-hidden />
          <div>
            <span>
              {report.is_latest
                ? report.progress.completed
                  ? "Previous mission complete"
                  : "Progress from your previous review"
                : "Mission status when this review was created"}
            </span>
            <h2>{report.progress.mission_title}</h2>
            <p>{report.progress.message}</p>
            {!report.is_latest ? <small>This is a historical check from when this report was created.</small> : null}
          </div>
          <StatusPill tone={report.progress.completed ? "good" : "warning"}>
            {report.progress.completed ? "Completed" : "Keep going"}
          </StatusPill>
        </section>
      ) : null}

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

      {practiceDrills[0] ? (
        <section className="primary-drill">
          <span>Practice this next</span>
          <h2>{practiceDrills[0].title}</h2>
          <p>{practiceDrills[0].how_to_practice}</p>
        </section>
      ) : null}

      {report.benchmark_context ? (
        <section className="benchmark-strip">
          <div>
            <span>{report.benchmark_context.source === "cohort" ? "Compared with similar matches" : "Practical role targets"}</span>
            <strong>{report.benchmark_context.label}</strong>
            <small>
              {report.benchmark_context.sample_size
                ? `${report.benchmark_context.sample_size} anonymized reports`
                : "A transparent role guideline until enough similar reports exist"}
            </small>
          </div>
          <div className="benchmark-metrics">
            {report.benchmark_context.metrics.slice(0, 3).map((metric) => (
              <article key={metric.metric}>
                <span>{metric.label}</span>
                <strong>{metric.user_value}</strong>
                <small>
                  {metric.percentile != null ? `${metric.percentile}th percentile` : `Target ${metric.comparison_value}`}
                </small>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {itemReview?.checkpoints?.length ? (
        <section className="item-lesson-card">
          <div className="item-lesson-header">
            <div>
              <span>Item timing lesson</span>
              <h2>What your build had to answer</h2>
              <p>{itemReview.main_lesson}</p>
            </div>
            <ShieldAlert size={28} aria-hidden />
          </div>
          <div className="item-checkpoint-grid">
            {itemReview.checkpoints.slice(0, 3).map((checkpoint) => (
              <article className="item-checkpoint" key={checkpoint.minute}>
                <div className="item-checkpoint-title">
                  <strong>{checkpoint.minute} min</strong>
                  <StatusPill tone={checkpoint.confidence === "high" ? "good" : "neutral"}>
                    {checkpoint.confidence} confidence
                  </StatusPill>
                </div>
                <ItemPills label="Your items" items={checkpoint.player_items} tone="info" />
                <ItemPills label="Enemy threats" items={checkpoint.enemy_key_items} tone="risk" />
                <p>{checkpoint.advice}</p>
              </article>
            ))}
          </div>
          <strong className="item-next-lesson">{itemReview.next_match_item_lesson}</strong>
        </section>
      ) : null}

      <details className="full-breakdown">
        <summary>
          <span>
            <strong>Full Match Breakdown</strong>
            <small>Mistakes, game-phase plan, strengths, checklist, and evidence</small>
          </span>
          <ChevronDown size={20} aria-hidden />
        </summary>
        <div className="breakdown-content">
      {report.comparison_context ? (
        <section className="context-strip">
          <div>
            <span>How this was judged</span>
            <strong>
              {report.comparison_context.hero} · {report.comparison_context.role} ·{" "}
              {report.comparison_context.duration_bucket}
            </strong>
          </div>
          <div className="context-tags">
            {report.comparison_context.rank_label ? <StatusPill>{report.comparison_context.rank_label}</StatusPill> : null}
            {report.comparison_context.patch ? <StatusPill>{report.comparison_context.patch}</StatusPill> : null}
          </div>
          <p>{report.comparison_context.baseline}</p>
        </section>
      ) : null}
      {report.timeline?.length ? (
        <section className="section-block">
          <div className="section-heading">
            <span>Match evidence timeline</span>
            <h2>What the parsed replay can confirm</h2>
          </div>
          <div className="timeline-list">
            {report.timeline.map((event, index) => (
              <article className={`timeline-event ${event.tone}`} key={`${event.minute}-${event.title}-${index}`}>
                <div className="timeline-minute">{event.minute}m</div>
                <CircleDot size={18} aria-hidden />
                <div>
                  <strong>{event.title}</strong>
                  <p>{event.detail}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : (
        <section className="inline-note">
          <CircleDot size={18} aria-hidden />
          Detailed event timing was not available for this match, so the report only uses confirmed final statistics.
        </section>
      )}

      {itemReview?.checkpoints?.length ? (
        <section className="section-block">
          <div className="section-heading">
            <span>Full item timing</span>
            <h2>Confirmed item windows</h2>
          </div>
          <div className="item-detail-list">
            {itemReview.checkpoints.map((checkpoint) => (
              <article className="item-detail-row" key={`detail-${checkpoint.minute}`}>
                <div>
                  <strong>{checkpoint.minute} min</strong>
                  <span>{checkpoint.enemy_threats.length ? checkpoint.enemy_threats.join(", ") : "No major enemy threat category"}</span>
                </div>
                <ItemPills label="Answers" items={checkpoint.player_answers} tone="good" />
                <p>{checkpoint.advice}</p>
              </article>
            ))}
          </div>
          <section className="limitation-note">
            <strong>Item timing limits</strong>
            <p>{itemReview.limitations.join(" ")}</p>
          </section>
        </section>
      ) : null}

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
              <span className="mistake-confidence">
                {mistake.confidence ?? "medium"} confidence · {(mistake.evidence_source ?? "final_stats").replaceAll("_", " ")}
              </span>
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
            <span>Game-phase plan</span>
            <h2>What to focus on through the match</h2>
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

      {practiceDrills.length > 1 ? (
        <section className="section-block">
          <div className="section-heading">
            <span>Practice Drills</span>
            <h2>How to improve this, not just read it</h2>
          </div>
          <div className="drill-grid">
            {practiceDrills.slice(1).map((drill) => (
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
        <strong>What this review can and cannot see</strong>
        <p>{report.limitations.join(" ")}</p>
      </section>
        </div>
      </details>

      {report.reflection_prompt ? (
        <section className="reflection-card">
          <div>
            <span>Before the next queue</span>
            <h2>One quick reflection</h2>
            <p>{report.reflection_prompt}</p>
          </div>
        </section>
      ) : null}

      <ReportFeedback reportId={report.id} initial={report.feedback} />

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

function ItemPills({
  label,
  items,
  tone
}: {
  label: string;
  items: string[];
  tone: "good" | "risk" | "info";
}) {
  return (
    <div className="item-pill-group">
      <span>{label}</span>
      <div>
        {items.length ? (
          items.map((item) => (
            <span className={`item-pill ${tone}`} key={item}>
              {item}
            </span>
          ))
        ) : (
          <span className="item-pill muted">None confirmed</span>
        )}
      </div>
    </div>
  );
}
