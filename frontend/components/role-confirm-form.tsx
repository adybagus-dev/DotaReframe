"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Loader2 } from "lucide-react";
import type { PlayerSummary } from "@/lib/types";

const roles = ["Carry", "Mid", "Offlane", "Soft Support", "Hard Support"];

export function RoleConfirmForm({
  matchId,
  player,
  detectedRole
}: {
  matchId: string;
  player: PlayerSummary;
  detectedRole: string;
}) {
  const router = useRouter();
  const [role, setRole] = useState(roles.includes(detectedRole) ? detectedRole : "");
  const [loading, setLoading] = useState(false);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!role) return;
    setLoading(true);
    router.push(`/match/${matchId}/report/${player.player_slot}?role=${encodeURIComponent(role)}`);
  }

  return (
    <form className="role-confirm-card" onSubmit={submit}>
      <div className="role-player">
        <div className="hero-avatar info">{player.hero.slice(0, 1)}</div>
        <div>
          <span>Your hero</span>
          <h2>{player.hero}</h2>
          <p>{player.result} · KDA {player.kda} · {player.gpm} GPM</p>
        </div>
      </div>
      <label>
        <span>Which role did you play?</span>
        <select value={role} onChange={(event) => setRole(event.target.value)} required>
          <option value="" disabled>Choose role</option>
          {roles.map((item) => <option value={item} key={item}>{item}</option>)}
        </select>
      </label>
      <p className="role-help">Confirm this yourself because lane data cannot always tell Soft Support from Hard Support.</p>
      <button className="button primary" type="submit" disabled={!role || loading}>
        {loading ? <Loader2 size={18} className="spin" aria-hidden /> : <ArrowRight size={18} aria-hidden />}
        {loading ? "Building your review..." : "Review My Match"}
      </button>
    </form>
  );
}
