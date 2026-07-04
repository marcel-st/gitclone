import { useState, type JSX } from "react";

import { AccountsPage } from "./pages/accounts-page";
import { AuditPage } from "./pages/audit-page";
import { DestinationsPage } from "./pages/destinations-page";
import { LinksPage } from "./pages/links-page";
import { ReposPage } from "./pages/repos-page";
import { TargetsPage } from "./pages/targets-page";

type Tab = "accounts" | "targets" | "repos" | "destinations" | "links" | "audit";

const TABS: { key: Tab; label: string }[] = [
  { key: "accounts", label: "Accounts" },
  { key: "targets", label: "Targets" },
  { key: "repos", label: "Repos" },
  { key: "destinations", label: "Destinations" },
  { key: "links", label: "Push links" },
  { key: "audit", label: "Audit" },
];

export function App(): JSX.Element {
  const [tab, setTab] = useState<Tab>("targets");

  return (
    <div className="app">
      <header className="top">
        <h1>gitclone</h1>
        <nav>
          {TABS.map((t) => (
            <button
              key={t.key}
              className={tab === t.key ? "tab active" : "tab"}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>
      <main>
        {tab === "accounts" ? <AccountsPage /> : null}
        {tab === "targets" ? <TargetsPage /> : null}
        {tab === "repos" ? <ReposPage /> : null}
        {tab === "destinations" ? <DestinationsPage /> : null}
        {tab === "links" ? <LinksPage /> : null}
        {tab === "audit" ? <AuditPage /> : null}
      </main>
    </div>
  );
}
