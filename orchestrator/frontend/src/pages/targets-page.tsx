import { useState, type JSX } from "react";

import { api } from "../api/client";
import { DataTable, type Column } from "../components/data-table";
import { Section } from "../components/section";
import { useCollection } from "../hooks/use-collection";
import type { DiscoverySummary, GithubAccount, TargetKind, TrackedTarget } from "../types";

const PATH = "/mirrors/targets/";

export function TargetsPage(): JSX.Element {
  const targets = useCollection<TrackedTarget>(PATH);
  const accounts = useCollection<GithubAccount>("/accounts/");
  const [account, setAccount] = useState<string>("");
  const [kind, setKind] = useState<TargetKind>("self_all");
  const [login, setLogin] = useState<string>("");
  const [repo, setRepo] = useState<string>("");
  const [formError, setFormError] = useState<string | null>(null);
  const [discovering, setDiscovering] = useState<boolean>(false);
  const [summary, setSummary] = useState<DiscoverySummary | null>(null);

  const add = async (): Promise<void> => {
    setFormError(null);
    try {
      await api.post(PATH, {
        account,
        kind,
        github_login: kind === "user_all" ? login : "",
        repo_full_name: kind === "repo" ? repo : "",
        enabled: true,
      });
      setLogin("");
      setRepo("");
      await targets.refresh();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : String(err));
    }
  };

  const discover = async (): Promise<void> => {
    setDiscovering(true);
    setFormError(null);
    try {
      setSummary(await api.post<DiscoverySummary>(`${PATH}discover/`));
    } catch (err) {
      setFormError(err instanceof Error ? err.message : String(err));
    } finally {
      setDiscovering(false);
    }
  };

  const remove = async (id: string): Promise<void> => {
    await api.remove(`${PATH}${id}/`);
    await targets.refresh();
  };

  const columns: Column<TrackedTarget>[] = [
    { header: "Kind", render: (r) => r.kind },
    { header: "Login / Repo", render: (r) => r.repo_full_name || r.github_login || "—" },
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

  const actions = (
    <button onClick={() => void discover()} disabled={discovering}>
      {discovering ? "discovering…" : "run discovery"}
    </button>
  );

  return (
    <Section title="Tracked targets" actions={actions} error={targets.error ?? formError}>
      {summary ? (
        <p className="muted">
          Last run: {summary.repos_seen} repos across {summary.targets} targets, {summary.errors} errors.
        </p>
      ) : null}
      <div className="form-row">
        <select value={account} onChange={(e) => setAccount(e.target.value)}>
          <option value="">select account…</option>
          {accounts.items.map((a) => (
            <option key={a.id} value={a.id}>
              {a.login}
            </option>
          ))}
        </select>
        <select value={kind} onChange={(e) => setKind(e.target.value as TargetKind)}>
          <option value="self_all">all my repos</option>
          <option value="user_all">all of a user</option>
          <option value="repo">single repo</option>
        </select>
        {kind === "user_all" ? (
          <input placeholder="github login" value={login} onChange={(e) => setLogin(e.target.value)} />
        ) : null}
        {kind === "repo" ? (
          <input placeholder="owner/name" value={repo} onChange={(e) => setRepo(e.target.value)} />
        ) : null}
        <button onClick={() => void add()} disabled={!account}>
          add
        </button>
      </div>
      <DataTable columns={columns} rows={targets.items} rowKey={(r) => r.id} />
    </Section>
  );
}
