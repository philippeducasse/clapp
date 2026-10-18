export enum DiscoveryRunStatus {
  QUEUED = "QUEUED",
  RUNNING = "RUNNING",
  DONE = "DONE",
  FAILED = "FAILED",
  CANCELLED = "CANCELLED",
}

export enum DiscoveryOrgType {
  FESTIVAL = "FESTIVAL",
  RESIDENCY = "RESIDENCY",
  VENUE = "VENUE",
}

export enum DiscoveryCandidateState {
  PENDING = "PENDING",
  ACCEPTED = "ACCEPTED",
  DISMISSED = "DISMISSED",
  ALREADY_KNOWN = "ALREADY_KNOWN",
  UNRESOLVED = "UNRESOLVED",
}

export enum DismissReason {
  NOT_RELEVANT = "NOT_RELEVANT",
  WRONG_REGION = "WRONG_REGION",
  DEFUNCT = "DEFUNCT",
  DUPLICATE = "DUPLICATE",
  OTHER = "OTHER",
}

export const DISMISS_REASON_LABELS: Record<DismissReason, string> = {
  [DismissReason.NOT_RELEVANT]: "Not relevant",
  [DismissReason.WRONG_REGION]: "Wrong region",
  [DismissReason.DEFUNCT]: "No longer exists",
  [DismissReason.DUPLICATE]: "Duplicate",
  [DismissReason.OTHER]: "Other",
};

export interface DiscoveryProgressLine {
  at: string;
  step: string;
  message: string;
}

export interface DiscoveryCounters {
  searches?: number;
  pages?: number;
  llmCalls?: number;
  leads?: number;
  leadsMissing?: number;
  candidates?: number;
}

export interface DiscoveryPlan {
  urls?: string[];
  goal?: string;
  orgTypes?: DiscoveryOrgType[];
  countries?: string[];
  queries?: string[];
}

export interface DiscoveryRun {
  id: number;
  startingPoint: string;
  status: DiscoveryRunStatus;
  isActive: boolean;
  cancelRequested: boolean;
  plan: DiscoveryPlan;
  progress: DiscoveryProgressLine[];
  counters: DiscoveryCounters;
  errors: string[];
  error: string;
  createdBy: string | null;
  createdAt: string;
  startedAt: string | null;
  finishedAt: string | null;
  lastHeartbeatAt: string | null;
}

/** One hop of `foundVia`, or one page in `sources`. */
export interface DiscoveryEvidence {
  url: string;
  kind?: string;
  title?: string;
  snippet?: string;
}

export interface DiscoveryContact {
  name: string;
  email: string;
  role: string;
}

export interface DiscoveryCandidate {
  id: number;
  run: number | null;
  orgType: DiscoveryOrgType;
  state: DiscoveryCandidateState;
  dismissReason: DismissReason | "";
  name: string;
  description: string;
  country: string;
  town: string;
  websiteUrl: string;
  domain: string;
  subtype: string;
  applicationType: string;
  applicationUrl: string;
  startDate: string | null;
  endDate: string | null;
  estimatedStartDate: string | null;
  approximateDate: string;
  applicationDateStart: string;
  applicationDateEnd: string;
  contacts: DiscoveryContact[];
  foundVia: DiscoveryEvidence[];
  sources: DiscoveryEvidence[];
  relevanceReason: string;
  createdSeed: { orgType: DiscoveryOrgType; id: number } | null;
  createdAt: string;
  reviewedAt: string | null;
}

/** Corrections the reviewer may make when accepting. */
export interface AcceptOverrides {
  orgType?: DiscoveryOrgType;
  name?: string;
  description?: string;
  country?: string;
  town?: string;
  websiteUrl?: string;
  subtype?: string;
  applicationType?: string;
}
