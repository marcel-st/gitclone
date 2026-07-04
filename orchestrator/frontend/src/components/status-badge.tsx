import type { JSX } from "react";

import type { SyncStatus } from "../types";

interface StatusBadgeProps {
  status: SyncStatus;
}

export function StatusBadge({ status }: StatusBadgeProps): JSX.Element {
  return <span className={`badge badge-${status}`}>{status}</span>;
}
