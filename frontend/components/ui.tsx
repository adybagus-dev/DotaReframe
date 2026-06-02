import Link from "next/link";
import type { LucideIcon } from "lucide-react";

type ButtonLinkProps = {
  href: string;
  children: React.ReactNode;
  variant?: "primary" | "secondary";
  icon?: LucideIcon;
};

export function ButtonLink({ href, children, variant = "primary", icon: Icon }: ButtonLinkProps) {
  return (
    <Link className={`button ${variant}`} href={href}>
      {Icon ? <Icon size={18} aria-hidden /> : null}
      {children}
    </Link>
  );
}

export function StatusPill({
  children,
  tone = "neutral"
}: {
  children: React.ReactNode;
  tone?: "good" | "risk" | "warning" | "info" | "neutral";
}) {
  return <span className={`pill ${tone}`}>{children}</span>;
}

export function EmptyState({
  title,
  body,
  action
}: {
  title: string;
  body: string;
  action?: React.ReactNode;
}) {
  return (
    <section className="empty-state">
      <h2>{title}</h2>
      <p>{body}</p>
      {action ? <div className="empty-action">{action}</div> : null}
    </section>
  );
}
