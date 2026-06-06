import { LoadingView } from "@/components/loading-view";

export default function ReportsLoading() {
  return (
    <LoadingView
      active="saved-reports"
      eyebrow="Saved Reports"
      title="Opening saved reports"
      body="Loading your coaching history from the database."
      cards={3}
    />
  );
}
