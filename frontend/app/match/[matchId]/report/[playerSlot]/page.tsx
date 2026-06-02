import { AppShell } from "@/components/app-shell";
import { ReportView } from "@/components/report-view";
import { createOrGetReport } from "@/lib/api";

type PageProps = {
  params: Promise<{ matchId: string; playerSlot: string }>;
};

export default async function GeneratedReportPage({ params }: PageProps) {
  const { matchId, playerSlot } = await params;
  const report = await createOrGetReport(matchId, playerSlot);

  return (
    <AppShell active="new-review">
      <ReportView report={report} />
    </AppShell>
  );
}
