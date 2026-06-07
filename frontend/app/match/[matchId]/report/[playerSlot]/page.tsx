import { AppShell } from "@/components/app-shell";
import { ReportLoader } from "@/components/report-loader";

type PageProps = {
  params: Promise<{ matchId: string; playerSlot: string }>;
  searchParams: Promise<{ role?: string; accountId?: string }>;
};

export default async function GeneratedReportPage({ params, searchParams }: PageProps) {
  const { matchId, playerSlot } = await params;
  const { role, accountId } = await searchParams;

  return (
    <AppShell active="new-review">
      <ReportLoader accountId={accountId} matchId={matchId} playerSlot={playerSlot} role={role} />
    </AppShell>
  );
}
