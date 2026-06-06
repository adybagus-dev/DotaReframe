"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronRight, Loader2 } from "lucide-react";
import type { PlayerSummary } from "@/lib/types";

const roleOptions = ["Carry", "Mid", "Offlane", "Soft Support", "Hard Support"];

function defaultRole(role?: string) {
  if (role === "Safe Lane") return "Carry";
  if (role === "Mid Lane") return "Mid";
  if (role === "Off Lane") return "Offlane";
  return "";
}

export function PlayerReviewForm({
  player,
  matchId,
  tone
}: {
  player: PlayerSummary;
  matchId: string;
  tone: "radiant" | "dire";
}) {
  const router = useRouter();
  const [role, setRole] = useState(defaultRole(player.role));
  const [loading, setLoading] = useState(false);

  function submitReview(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!role || loading) return;
    setLoading(true);
    router.push(`/match/${matchId}/report/${player.player_slot}?role=${encodeURIComponent(role)}`);
  }

  return (
    <form className={`player-card${loading ? " is-loading" : ""}`} onSubmit={submitReview}>
      <div className={`hero-avatar ${tone}`}>{player.hero.slice(0, 1)}</div>
      <div className="player-main">
        <h3>{player.hero}</h3>
        <p>
          {player.team} · {player.result}
        </p>
      </div>
      <div className="player-stats">
        <span>KDA: {player.kda}</span>
        <span>GPM: {player.gpm}</span>
      </div>
      <label className="role-picker">
        <span>Review this hero as</span>
        <select
          value={role}
          onChange={(event) => setRole(event.target.value)}
          required
          disabled={loading}
        >
          <option value="" disabled>
            Choose role
          </option>
          {roleOptions.map((option) => (
            <option value={option} key={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
      <button className="player-action" type="submit" disabled={loading || !role}>
        <span>{loading ? "Generating report..." : "Review This Role"}</span>
        {loading ? <Loader2 size={16} aria-hidden className="spin" /> : <ChevronRight size={16} aria-hidden />}
      </button>
    </form>
  );
}
