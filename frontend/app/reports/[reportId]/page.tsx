import { AppShell } from "@/components/app-shell";
import { ButtonLink, EmptyState } from "@/components/ui";
import { ReportView } from "@/components/report-view";
import { getSavedReport } from "@/lib/api";

type PageProps = {
  params: Promise<{ reportId: string }>;
};

export default async function SavedReportPage({ params }: PageProps) {
  const { reportId } = await params;
  try {
    const report = await getSavedReport(reportId);

    return (
      <AppShell active="saved-reports">
        <ReportView report={report} savedDetail />
      </AppShell>
    );
  } catch {
    return (
      <AppShell active="saved-reports">
        <div className="page-stack">
          <EmptyState
            title="Saved report unavailable"
            body="This report could not be loaded right now. Try refreshing or open another saved report."
            action={<ButtonLink href="/reports">Back to Saved Reports</ButtonLink>}
          />
        </div>
      </AppShell>
    );
  }
}
