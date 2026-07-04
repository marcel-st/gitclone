import type { JSX } from "react";

import { DataTable, type Column } from "../components/data-table";
import { Section } from "../components/section";
import { useCollection } from "../hooks/use-collection";
import type { AuditLogEntry } from "../types";

export function AuditPage(): JSX.Element {
  const { items, error, refresh } = useCollection<AuditLogEntry>("/destinations/audit/");

  const columns: Column<AuditLogEntry>[] = [
    { header: "When", render: (r) => new Date(r.created_at).toLocaleString() },
    { header: "Actor", render: (r) => r.actor },
    { header: "Action", render: (r) => r.action },
    { header: "Target", render: (r) => r.target },
    { header: "Detail", render: (r) => r.detail },
  ];

  const actions = <button onClick={() => void refresh()}>refresh</button>;

  return (
    <Section title="Audit log" actions={actions} error={error}>
      <DataTable columns={columns} rows={items} rowKey={(r) => r.id} empty="No actions recorded yet." />
    </Section>
  );
}
