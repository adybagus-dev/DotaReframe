import Link from "next/link";
import { Users } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PlayerReviewForm } from "@/components/player-review-form";
import { getPlayers } from "@/lib/api";
import type { PlayerSummary } from "@/lib/types";

type PageProps = {
  params: Promise<{ matchId: string }>;
  searchParams: Promise<{ accountId?: string }>;
};

export default async function PlayerSelectionPage({ params, searchParams }: PageProps) {
  const { matchId } = await params;
  const { accountId } = await searchParams;
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
            <strong>{players.length} players found</strong>
          </div>
        </section>

        <div className="team-grid">
          <TeamColumn title="Radiant" tone="radiant" players={radiant} matchId={matchId} accountId={accountId} />
          <TeamColumn title="Dire" tone="dire" players={dire} matchId={matchId} accountId={accountId} />
        </div>
      </div>
    </AppShell>
  );
}

function TeamColumn({
  title,
  tone,
  players,
  matchId,
  accountId
}: {
  title: string;
  tone: "radiant" | "dire";
  players: PlayerSummary[];
  matchId: string;
  accountId?: string;
}) {
  return (
    <section className="team-column">
      <h2 className={tone}>
        <Users size={20} aria-hidden />
        {title}
      </h2>
      <div className="player-grid">
        {players.map((player) => (
          <PlayerReviewForm
            player={player}
            matchId={matchId}
            tone={tone}
            accountId={accountId}
            key={player.player_slot}
          />
        ))}
      </div>
    </section>
  );
}
