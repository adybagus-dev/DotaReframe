"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, ArrowRight, ClipboardList, Loader2, Search } from "lucide-react";

export function MatchIdForm({ connected }: { connected: boolean }) {
  const router = useRouter();
  const [matchId, setMatchId] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const validation = useMemo(() => {
    if (!submitted && !matchId.trim()) return "";
    return /^\d{7,12}$/.test(matchId.trim()) ? "" : "Use numbers only, for example 8123456789.";
  }, [matchId, submitted]);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
    if (!matchId.trim() || validation) return;
    setLoading(true);
    router.push(connected ? `/match/${matchId.trim()}/review` : `/match/${matchId.trim()}/players`);
  }

  return (
    <section className="input-panel" id="manual-review">
      <div className="input-copy">
        <ClipboardList size={34} aria-hidden />
        <h2>Review a specific match</h2>
        <p>Paste the match ID from Dota 2 Match History or OpenDota.</p>
      </div>
      <form className="match-form" onSubmit={submit}>
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
        {validation ? <p className="field-error"><AlertCircle size={16} aria-hidden />{validation}</p> : null}
        <button className="button primary" disabled={loading || !matchId.trim() || Boolean(validation)} type="submit">
          {loading ? <Loader2 size={18} className="spin" aria-hidden /> : <ArrowRight size={18} aria-hidden />}
          {loading ? "Opening match..." : connected ? "Confirm My Role" : "Choose My Hero"}
        </button>
      </form>
    </section>
  );
}
