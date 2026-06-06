import { LoadingView } from "@/components/loading-view";

export default function MatchLoading() {
  return (
    <LoadingView
      active="new-review"
      eyebrow="New Review"
      title="Reading match data"
      body="Fetching players and match statistics from OpenDota."
      cards={6}
    />
  );
}
