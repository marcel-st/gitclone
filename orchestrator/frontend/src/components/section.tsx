import type { JSX, ReactNode } from "react";

interface SectionProps {
  title: string;
  actions?: ReactNode;
  error?: string | null;
  children: ReactNode;
}

export function Section({ title, actions, error, children }: SectionProps): JSX.Element {
  return (
    <section className="card">
      <header className="card-head">
        <h2>{title}</h2>
        <div className="card-actions">{actions}</div>
      </header>
      {error ? <p className="error">{error}</p> : null}
      {children}
    </section>
  );
}
