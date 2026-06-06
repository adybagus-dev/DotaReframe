import { LoadingView } from "@/components/loading-view";

export default function Loading() {
  return (
    <LoadingView
      active="new-review"
      eyebrow="DotaReframe"
      title="Loading your review"
      body="Getting the next screen ready."
    />
  );
}
