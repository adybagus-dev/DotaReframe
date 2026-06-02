import Link from "next/link";
import { Activity, Archive, ClipboardList } from "lucide-react";

type AppShellProps = {
  active: "new-review" | "saved-reports";
  children: React.ReactNode;
};

export function AppShell({ active, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <Link href="/match" className="brand">
            <span className="brand-mark">D</span>
            <span>
              <strong>DotaReframe</strong>
              <small>See it differently</small>
            </span>
          </Link>
          <nav className="nav-list" aria-label="Main navigation">
            <Link className={active === "new-review" ? "nav-item active" : "nav-item"} href="/match">
              <ClipboardList size={18} aria-hidden />
              New Review
            </Link>
            <Link className={active === "saved-reports" ? "nav-item active" : "nav-item"} href="/reports">
              <Archive size={18} aria-hidden />
              Saved Reports
            </Link>
          </nav>
        </div>
        <div className="status-card">
          <Activity size={16} aria-hidden />
          <span>Backend: Online</span>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
