import { useState, type JSX } from "react";

import { api } from "../api/client";
import { DataTable, type Column } from "../components/data-table";
import { Section } from "../components/section";
import { useCollection } from "../hooks/use-collection";
import type { GithubAccount } from "../types";

const PATH = "/accounts/";

export function AccountsPage(): JSX.Element {
  const { items, error, refresh } = useCollection<GithubAccount>(PATH);
  const [login, setLogin] = useState<string>("");
  const [pat, setPat] = useState<string>("");
  const [isSelf, setIsSelf] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  const add = async (): Promise<void> => {
    setFormError(null);
    try {
      await api.post(PATH, { login, pat, is_self: isSelf, enabled: true });
      setLogin("");
      setPat("");
      setIsSelf(false);
      await refresh();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : String(err));
    }
  };

  const remove = async (id: string): Promise<void> => {
    await api.remove(`${PATH}${id}/`);
    await refresh();
  };

  const columns: Column<GithubAccount>[] = [
    { header: "Login", render: (r) => r.login },
    { header: "Self", render: (r) => (r.is_self ? "yes" : "") },
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
    <Section title="GitHub accounts" error={error ?? formError}>
      <div className="form-row">
        <input placeholder="github login" value={login} onChange={(e) => setLogin(e.target.value)} />
        <input
          placeholder="read-only PAT"
          type="password"
          value={pat}
          onChange={(e) => setPat(e.target.value)}
        />
        <label className="check">
          <input type="checkbox" checked={isSelf} onChange={(e) => setIsSelf(e.target.checked)} />
          is me
        </label>
        <button onClick={() => void add()} disabled={!login || !pat}>
          add
        </button>
      </div>
      <DataTable columns={columns} rows={items} rowKey={(r) => r.id} />
    </Section>
  );
}
