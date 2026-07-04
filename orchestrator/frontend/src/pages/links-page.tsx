import { useState, type JSX } from "react";

import { api } from "../api/client";
import { DataTable, type Column } from "../components/data-table";
import { Section } from "../components/section";
import { useCollection } from "../hooks/use-collection";
import type { MirroredRepo, PushDestination, PushMirrorLink } from "../types";

const PATH = "/destinations/links/";

export function LinksPage(): JSX.Element {
  const links = useCollection<PushMirrorLink>(PATH);
  const repos = useCollection<MirroredRepo>("/mirrors/repos/");
  const destinations = useCollection<PushDestination>("/destinations/destinations/");
  const [repo, setRepo] = useState<string>("");
  const [destination, setDestination] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const repoName = (id: string): string =>
    repos.items.find((r) => r.id === id)?.source_full_name ?? id;
  const destName = (id: string): string =>
    destinations.items.find((d) => d.id === id)?.name ?? id;

  const add = async (): Promise<void> => {
    setError(null);
    try {
      await api.post(PATH, { repo, destination, require_confirmation: true });
      await links.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const push = async (link: PushMirrorLink): Promise<void> => {
    // Push force-updates the remote — require an explicit confirmation.
    const ok = window.confirm(
      `Push ${repoName(link.repo)} to ${destName(link.destination)}?\n\n` +
        "This force-updates the remote and overwrites its history.",
    );
    if (!ok) {
      return;
    }
    setError(null);
    try {
      await api.post(`${PATH}${link.id}/push/`, { confirmed: true });
      await links.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const remove = async (id: string): Promise<void> => {
    await api.remove(`${PATH}${id}/`);
    await links.refresh();
  };

  const columns: Column<PushMirrorLink>[] = [
    { header: "Repo", render: (r) => repoName(r.repo) },
    { header: "Destination", render: (r) => destName(r.destination) },
    { header: "Last pushed", render: (r) => (r.last_pushed_at ? new Date(r.last_pushed_at).toLocaleString() : "never") },
    {
      header: "",
      render: (r) => (
        <span className="row-actions">
          <button onClick={() => void push(r)}>push</button>
          <button className="danger" onClick={() => void remove(r.id)}>
            delete
          </button>
        </span>
      ),
    },
  ];

  return (
    <Section title="Push mirror links" error={links.error ?? error}>
      <div className="form-row">
        <select value={repo} onChange={(e) => setRepo(e.target.value)}>
          <option value="">select repo…</option>
          {repos.items.map((r) => (
            <option key={r.id} value={r.id}>
              {r.source_full_name}
            </option>
          ))}
        </select>
        <select value={destination} onChange={(e) => setDestination(e.target.value)}>
          <option value="">select destination…</option>
          {destinations.items.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
        <button onClick={() => void add()} disabled={!repo || !destination}>
          link
        </button>
      </div>
      <DataTable columns={columns} rows={links.items} rowKey={(r) => r.id} empty="No push links yet." />
    </Section>
  );
}
