import {
  DiscoveryCandidate,
  DiscoveryEvidence,
  DiscoveryOrgType,
  DiscoveryRun,
  DiscoveryRunStatus,
} from "@/interfaces/entities/Discovery";

const HOP_LABELS: Record<string, string> = {
  start: "Starting point",
  search: "Search",
  artist_site: "Artist site",
  aggregator: "List",
  calendar: "Calendar",
  listing: "Listing",
  org_site: "Website",
  festival_site: "Festival site",
  residency_site: "Residency site",
  venue_site: "Venue site",
  contact: "Contact page",
  application: "Application page",
};

export const hopLabel = (kind?: string): string => {
  if (!kind) return "Page";
  const label = HOP_LABELS[kind.toLowerCase()];
  if (label) return label;
  const words = kind.toLowerCase().replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
};

/** "Artist site → Calendar → Festival site → Contact page" */
export const foundViaSummary = (hops: DiscoveryEvidence[]): string =>
  hops.map((hop) => hopLabel(hop.kind)).join(" → ");

export const ORG_TYPE_LABELS: Record<DiscoveryOrgType, string> = {
  [DiscoveryOrgType.FESTIVAL]: "Festival",
  [DiscoveryOrgType.RESIDENCY]: "Residency",
  [DiscoveryOrgType.VENUE]: "Venue",
};

const ORG_TYPE_PATHS: Record<DiscoveryOrgType, string> = {
  [DiscoveryOrgType.FESTIVAL]: "/festivals",
  [DiscoveryOrgType.RESIDENCY]: "/residencies",
  [DiscoveryOrgType.VENUE]: "/venues",
};

/** Link to the seed created when the candidate was accepted. */
export const seedUrl = (candidate: DiscoveryCandidate): string | null =>
  candidate.createdSeed
    ? `${ORG_TYPE_PATHS[candidate.createdSeed.orgType]}/${candidate.createdSeed.id}`
    : null;

export const candidateLocation = (candidate: DiscoveryCandidate): string =>
  [candidate.town, candidate.country].filter(Boolean).join(", ");

/** "11 Jun 2027 – 13 Jun 2027", or the approximate date, or "". */
export const candidateDates = (candidate: DiscoveryCandidate): string => {
  const format = (value: string) =>
    new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  if (candidate.startDate && candidate.endDate && candidate.endDate !== candidate.startDate) {
    return `${format(candidate.startDate)} – ${format(candidate.endDate)}`;
  }
  if (candidate.startDate) return format(candidate.startDate);
  return candidate.approximateDate;
};

export const candidateApplicationDates = (candidate: DiscoveryCandidate): string => {
  const { applicationDateStart: start, applicationDateEnd: end } = candidate;
  if (start && end) return `${start} → ${end}`;
  if (end) return `until ${end}`;
  if (start) return `from ${start}`;
  return "";
};

export const RUN_STATUS_STYLES: Record<DiscoveryRunStatus, string> = {
  [DiscoveryRunStatus.QUEUED]: "bg-slate-100 text-slate-700 border-slate-200",
  [DiscoveryRunStatus.RUNNING]: "bg-sky-100 text-sky-700 border-sky-200",
  [DiscoveryRunStatus.DONE]: "bg-green-100 text-green-700 border-green-200",
  [DiscoveryRunStatus.FAILED]: "bg-red-100 text-red-700 border-red-200",
  [DiscoveryRunStatus.CANCELLED]: "bg-amber-100 text-amber-700 border-amber-200",
};

export const runLabel = (run: DiscoveryRun): string => {
  const text = run.startingPoint.length > 60 ? `${run.startingPoint.slice(0, 60)}…` : run.startingPoint;
  return `#${run.id} · ${run.status.toLowerCase()} · ${text}`;
};

export const COUNTER_LABELS: { key: keyof DiscoveryRun["counters"]; label: string }[] = [
  { key: "pages", label: "Pages" },
  { key: "searches", label: "Searches" },
  { key: "llmCalls", label: "LLM calls" },
  { key: "leads", label: "Leads" },
  { key: "leadsMissing", label: "Missing" },
  { key: "candidates", label: "Candidates" },
];
