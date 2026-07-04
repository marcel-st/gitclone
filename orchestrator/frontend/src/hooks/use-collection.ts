// Loads a list endpoint and exposes refresh + loading/error state.
import { useCallback, useEffect, useState } from "react";

import { api } from "../api/client";

interface Collection<T> {
  items: T[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useCollection<T>(path: string): Collection<T> {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      setItems(await api.list<T>(path));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { items, loading, error, refresh };
}
