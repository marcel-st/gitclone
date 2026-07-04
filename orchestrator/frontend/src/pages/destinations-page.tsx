import { useState, type JSX } from "react";

import { api } from "../api/client";
import { DataTable, type Column } from "../components/data-table";
import { Section } from "../components/section";
import { useCollection } from "../hooks/use-collection";
import type { DestinationType, PushDestination } from "../types";

const PATH = "/destinations/destinations/";

export function DestinationsPage(): JSX.Element {
  const { items, error, refresh } = useCollection<PushDestination>(PATH);
  const [name, setName] = useState<string>("");
  const [type, setType] = useState<DestinationType>("github");
  const [remoteUrl, setRemoteUrl] = useState<string>("");
  const [username, setUsername] = useState<string>("");
  const [token, setToken] = useState<string>("");
  const [formError, setFormError] = useState<string | null>(null);

  const add = async (): Promise<void> => {
    setFormError(null);
    try {
      await api.post(PATH, {
        name,
        type,
        remote_url: remoteUrl,
        remote_username: username,
        write_token: token,
        enabled: true,
      });
      setName("");
      setRemoteUrl("");
      setUsername("");
      setToken("");
      await refresh();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : String(err));
    }
  };

  const remove = async (id: string): Promise<void> => {
    await api.remove(`${PATH}${id}/`);
    await refresh();
  };

  const columns: Column<PushDestination>[] = [
    { header: "Name", render: (r) => r.name },
    { header: "Type", render: (r) => r.type },
    { header: "Remote", render: (r) => r.remote_url },
    { header: "Enabled", render: (r) => (r.enabled ? "yes" : "no") },
    {
      header: "",
      render: (r) => (
        <button className="danger" onClick={() => void remove(r.id)}>
          delete
        </button>
      ),
    },
  ];

  return (
    <Section title="Push destinations" error={error ?? formError}>
      <div className="form-row">
        <input placeholder="name" value={name} onChange={(e) => setName(e.target.value)} />
        <select value={type} onChange={(e) => setType(e.target.value as DestinationType)}>
          <option value="github">GitHub</option>
          <option value="gitlab">GitLab</option>
          <option value="gitea">Gitea</option>
        </select>
        <input placeholder="remote base url" value={remoteUrl} onChange={(e) => setRemoteUrl(e.target.value)} />
        <input placeholder="username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input placeholder="write token" type="password" value={token} onChange={(e) => setToken(e.target.value)} />
        <button onClick={() => void add()} disabled={!name || !remoteUrl || !token}>
          add
        </button>
      </div>
      <DataTable columns={columns} rows={items} rowKey={(r) => r.id} />
    </Section>
  );
}
