import Link from "next/link";
import { AlertTriangle, ChevronRight, Clock, Users } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { StatusPill } from "@/components/ui";
import { getPlayers } from "@/lib/api";
import type { PlayerSummary } from "@/lib/types";

type PageProps = {
  params: Promise<{ matchId: string }>;
};

const roleOptions = ["Carry", "Mid", "Offlane", "Soft Support", "Hard Support"];

function defaultRole(role?: string) {
  if (role === "Safe Lane") return "Carry";
  if (role === "Mid Lane") return "Mid";
  if (role === "Off Lane") return "Offlane";
  return "";
}

export default async function PlayerSelectionPage({ params }: PageProps) {
  const { matchId } = await params;
  const players = await getPlayers(matchId);
  const radiant = players.filter((player) => player.team === "Radiant");
  const dire = players.filter((player) => player.team === "Dire");

  return (
    <AppShell active="new-review">
      <div className="page-stack">
        <div className="page-heading split">
          <div>
            <span className="eyebrow">New Review / Players</span>
            <h1>Choose Your Hero</h1>
            <p>Pick the player you want DotaReframe to review.</p>
          </div>
          <Link href="/match" className="text-link">
            Back to Match Input
          </Link>
        </div>

        <section className="match-strip">
          <div>
            <span>Match {matchId}</span>
            <strong>
              <Clock size={18} aria-hidden />
              42 min
            </strong>
          </div>
          <div>
            <StatusPill tone="risk">Radiant lost</StatusPill>
            <StatusPill tone="good">Dire won</StatusPill>
          </div>
        </section>

        <section className="incomplete-note">
          <AlertTriangle size={18} aria-hidden />
          If OpenDota returns incomplete data, show a clear note and keep the cards readable.
        </section>

        <div className="team-grid">
          <TeamColumn title="Radiant" tone="radiant" players={radiant} matchId={matchId} />
          <TeamColumn title="Dire" tone="dire" players={dire} matchId={matchId} />
        </div>
      </div>
    </AppShell>
  );
}

function TeamColumn({
  title,
  tone,
  players,
  matchId
}: {
  title: string;
  tone: "radiant" | "dire";
  players: PlayerSummary[];
  matchId: string;
}) {
  return (
    <section className="team-column">
      <h2 className={tone}>
        <Users size={20} aria-hidden />
        {title}
      </h2>
      <div className="player-grid">
        {players.map((player) => (
          <form
            action={`/match/${matchId}/report/${player.player_slot}`}
            className="player-card"
            key={player.player_slot}
          >
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
              <select name="role" defaultValue={defaultRole(player.role)} required>
                <option value="" disabled>
                  Choose role
                </option>
                {roleOptions.map((role) => (
                  <option value={role} key={role}>
                    {role}
                  </option>
                ))}
              </select>
            </label>
            <button className="player-action" type="submit">
              Review This Role
              <ChevronRight size={16} aria-hidden />
            </button>
          </form>
        ))}
      </div>
    </section>
  );
}
