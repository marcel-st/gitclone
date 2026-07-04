// API shapes mirroring the orchestrator serializers.

export interface GithubAccount {
  id: string;
  login: string;
  is_self: boolean;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export type TargetKind = "self_all" | "user_all" | "repo";

export interface TrackedTarget {
  id: string;
  account: string;
  kind: TargetKind;
  github_login: string;
  repo_full_name: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export type SyncStatus = "pending" | "ok" | "error" | "skipped";

export interface MirroredRepo {
  id: string;
  source_full_name: string;
  forgejo_owner: string;
  forgejo_repo_name: string;
  is_private: boolean;
  size_bytes: number;
  last_sync_at: string | null;
  last_sync_status: SyncStatus;
  last_error: string;
  created_at: string;
}

export type DestinationType = "github" | "gitlab" | "gitea";

export interface PushDestination {
  id: string;
  name: string;
  type: DestinationType;
  remote_url: string;
  remote_username: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface PushMirrorLink {
  id: string;
  repo: string;
  destination: string;
  require_confirmation: boolean;
  last_pushed_at: string | null;
  created_at: string;
}

export interface AuditLogEntry {
  id: string;
  actor: string;
  action: string;
  target: string;
  detail: string;
  created_at: string;
}

export interface DiscoverySummary {
  targets: number;
  repos_seen: number;
  errors: number;
}
