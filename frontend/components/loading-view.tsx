import { Loader2 } from "lucide-react";
import { AppShell } from "./app-shell";

type LoadingViewProps = {
  active: "new-review" | "saved-reports";
  eyebrow: string;
  title: string;
  body: string;
  cards?: number;
};

export function LoadingView({ active, eyebrow, title, body, cards = 4 }: LoadingViewProps) {
  return (
    <AppShell active={active}>
      <div className="page-stack" aria-busy="true" aria-live="polite">
        <div className="page-heading">
          <span className="eyebrow">{eyebrow}</span>
          <h1>{title}</h1>
          <p>{body}</p>
        </div>

        <section className="loading-panel">
          <div className="loading-message">
            <Loader2 size={22} aria-hidden className="spin" />
            <div>
              <strong>Please wait</strong>
              <span>This can take a few seconds on the first request.</span>
            </div>
          </div>
          <div className="loading-grid" aria-hidden>
            {Array.from({ length: cards }, (_, index) => (
              <div className="loading-card" key={index}>
                <span className="skeleton skeleton-avatar" />
                <div>
                  <span className="skeleton skeleton-title" />
                  <span className="skeleton skeleton-line" />
                  <span className="skeleton skeleton-line short" />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
