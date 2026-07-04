import type { JSX } from "react";

import { DataTable, type Column } from "../components/data-table";
import { Section } from "../components/section";
import { StatusBadge } from "../components/status-badge";
import { useCollection } from "../hooks/use-collection";
import type { MirroredRepo } from "../types";

function mb(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ReposPage(): JSX.Element {
  const { items, error, refresh } = useCollection<MirroredRepo>("/mirrors/repos/");

  const columns: Column<MirroredRepo>[] = [
    { header: "Repo", render: (r) => r.source_full_name },
    { header: "Private", render: (r) => (r.is_private ? "yes" : "") },
    { header: "Size", render: (r) => mb(r.size_bytes) },
    { header: "Status", render: (r) => <StatusBadge status={r.last_sync_status} /> },
    { header: "Last sync", render: (r) => (r.last_sync_at ? new Date(r.last_sync_at).toLocaleString() : "—") },
    { header: "Error", render: (r) => (r.last_error ? <span className="error">{r.last_error}</span> : "") },
  ];

  const actions = <button onClick={() => void refresh()}>refresh</button>;

  return (
    <Section title="Mirrored repositories" actions={actions} error={error}>
      <DataTable columns={columns} rows={items} rowKey={(r) => r.id} empty="No repos mirrored yet — add a target and run discovery." />
    </Section>
  );
}
