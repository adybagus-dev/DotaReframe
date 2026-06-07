"use client";

import { useState } from "react";
import { Check, ThumbsDown, ThumbsUp } from "lucide-react";
import type { ReportFeedback as Feedback } from "@/lib/types";

const reasons = [
  ["wrong_role", "Wrong role"],
  ["weak_evidence", "Weak evidence"],
  ["too_generic", "Advice too generic"],
  ["hero_mismatch", "Does not fit this hero"]
] as const;

export function ReportFeedback({ reportId, initial }: { reportId: string; initial?: Feedback }) {
  const [feedback, setFeedback] = useState<Feedback | undefined>(initial);
  const [showReasons, setShowReasons] = useState(false);
  const [saving, setSaving] = useState(false);

  async function save(next: Feedback) {
    setSaving(true);
    const response = await fetch(`/api/me/reports/${reportId}/feedback`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(next)
    });
    if (response.ok) setFeedback(await response.json());
    setSaving(false);
  }

  return (
    <section className="feedback-card">
      <div>
        <span>Was this review useful?</span>
        <p>Your answer helps DotaReframe improve the coaching rules.</p>
      </div>
      <div className="feedback-actions">
        <button
          className={feedback?.helpful ? "feedback-button selected" : "feedback-button"}
          type="button"
          disabled={saving}
          onClick={() => { setShowReasons(false); void save({ helpful: true }); }}
        >
          {feedback?.helpful ? <Check size={17} aria-hidden /> : <ThumbsUp size={17} aria-hidden />}
          Helpful
        </button>
        <button
          className={feedback && !feedback.helpful ? "feedback-button selected risk" : "feedback-button"}
          type="button"
          disabled={saving}
          onClick={() => setShowReasons(true)}
        >
          <ThumbsDown size={17} aria-hidden />
          Not accurate
        </button>
      </div>
      {showReasons ? (
        <div className="feedback-reasons">
          <span>What felt wrong? Optional</span>
          {reasons.map(([value, label]) => (
            <button type="button" key={value} disabled={saving} onClick={() => void save({ helpful: false, reason: value })}>
              {label}
            </button>
          ))}
          <button type="button" disabled={saving} onClick={() => void save({ helpful: false })}>Skip reason</button>
        </div>
      ) : null}
    </section>
  );
}
