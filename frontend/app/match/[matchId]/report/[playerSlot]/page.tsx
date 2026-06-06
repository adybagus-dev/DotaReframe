import { AppShell } from "@/components/app-shell";
import { ReportView } from "@/components/report-view";
import { createOrGetReport } from "@/lib/api";

type PageProps = {
  params: Promise<{ matchId: string; playerSlot: string }>;
  searchParams: Promise<{ role?: string; accountId?: string }>;
};

export default async function GeneratedReportPage({ params, searchParams }: PageProps) {
  const { matchId, playerSlot } = await params;
  const { role, accountId } = await searchParams;
  const report = await createOrGetReport(matchId, playerSlot, role, accountId);

  return (
    <AppShell active="new-review">
      <ReportView report={report} />
    </AppShell>
  );
}
