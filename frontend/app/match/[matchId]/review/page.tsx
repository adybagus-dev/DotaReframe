import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { ButtonLink, EmptyState } from "@/components/ui";
import { RoleConfirmForm } from "@/components/role-confirm-form";
import { getReviewContext } from "@/lib/api";

type PageProps = { params: Promise<{ matchId: string }> };

export default async function ReviewContextPage({ params }: PageProps) {
  const { matchId } = await params;
  try {
    const context = await getReviewContext(matchId);
    return (
      <AppShell active="new-review">
        <div className="page-stack narrow-stack">
          <div className="page-heading">
            <span className="eyebrow">One quick check</span>
            <h1>Confirm your role</h1>
            <p>DotaReframe found your Steam player automatically. Your role decides which expectations are fair.</p>
          </div>
          <RoleConfirmForm matchId={matchId} player={context.player} detectedRole={context.detected_role} />
          <Link href="/match" className="text-link">Back to My Progress</Link>
        </div>
      </AppShell>
    );
  } catch {
    return (
      <AppShell active="new-review">
        <div className="page-stack narrow-stack">
          <EmptyState
            title="Role check unavailable"
            body="We could not load the fast review context right now. You can still review by choosing a player manually."
            action={<ButtonLink href={`/match/${matchId}/players`}>Choose Player Manually</ButtonLink>}
          />
          <Link href="/match" className="text-link">Back to Match Input</Link>
        </div>
      </AppShell>
    );
  }
}
