import { AppShell } from "@/components/app-shell";
import { ReportView } from "@/components/report-view";
import { getSavedReport } from "@/lib/api";

type PageProps = {
  params: Promise<{ reportId: string }>;
};

export default async function SavedReportPage({ params }: PageProps) {
  const { reportId } = await params;
  const report = await getSavedReport(reportId);

  return (
    <AppShell active="saved-reports">
      <ReportView report={report} savedDetail />
    </AppShell>
  );
}
