import { AppShell } from "@/components/app-shell";
import { ReportView } from "@/components/report-view";
import { createOrGetReport } from "@/lib/api";

type PageProps = {
  params: Promise<{ matchId: string; playerSlot: string }>;
  searchParams: Promise<{ role?: string }>;
};

export default async function GeneratedReportPage({ params, searchParams }: PageProps) {
  const { matchId, playerSlot } = await params;
  const { role } = await searchParams;
  const report = await createOrGetReport(matchId, playerSlot, role);

  return (
    <AppShell active="new-review">
      <ReportView report={report} />
    </AppShell>
  );
}
