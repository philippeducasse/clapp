import {
  AcceptOverrides,
  DiscoveryCandidate,
  DiscoveryCandidateState,
  DiscoveryRun,
  DismissReason,
} from "@/interfaces/entities/Discovery";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { fetchRequest, sendRequest, silentRequest } from "./fetchHelper";

/** Superusers only: the backend answers 403 to everyone else. */
export const discoveryEndpoint = "/api/discovery";

const startRun = (startingPoint: string): Promise<DiscoveryRun> =>
  sendRequest<{ startingPoint: string }, DiscoveryRun>(
    `${discoveryEndpoint}/runs`,
    { startingPoint },
    "POST",
    "Discovery started",
  );

const getRuns = (limit = 20): Promise<PaginatedResponse<DiscoveryRun>> =>
  fetchRequest<PaginatedResponse<DiscoveryRun>>(`${discoveryEndpoint}/runs?limit=${limit}`);

/** Used for polling: never shows a toast. */
const getRun = (id: number): Promise<DiscoveryRun> =>
  silentRequest<DiscoveryRun>(`${discoveryEndpoint}/runs/${id}`);

const cancelRun = (id: number): Promise<DiscoveryRun> =>
  sendRequest<object, DiscoveryRun>(
    `${discoveryEndpoint}/runs/${id}/cancel`,
    {},
    "POST",
    "Cancel requested",
  );

const getCandidates = (
  filters: { state?: DiscoveryCandidateState; run?: number } = {},
): Promise<PaginatedResponse<DiscoveryCandidate>> => {
  const params = new URLSearchParams({ limit: "200" });
  if (filters.state) params.set("state", filters.state);
  if (filters.run) params.set("run", filters.run.toString());
  return fetchRequest<PaginatedResponse<DiscoveryCandidate>>(
    `${discoveryEndpoint}/candidates?${params.toString()}`,
  );
};

const accept = (id: number, overrides: AcceptOverrides = {}): Promise<DiscoveryCandidate> =>
  sendRequest<AcceptOverrides, DiscoveryCandidate>(
    `${discoveryEndpoint}/candidates/${id}/accept`,
    overrides,
    "POST",
    "Added for all users",
  );

const dismiss = (id: number, reason: DismissReason): Promise<DiscoveryCandidate> =>
  sendRequest<{ reason: DismissReason }, DiscoveryCandidate>(
    `${discoveryEndpoint}/candidates/${id}/dismiss`,
    { reason },
    "POST",
    "Candidate dismissed",
  );

const restore = (id: number): Promise<DiscoveryCandidate> =>
  sendRequest<object, DiscoveryCandidate>(
    `${discoveryEndpoint}/candidates/${id}/restore`,
    {},
    "POST",
    "Candidate restored",
  );

export const discoveryApiService = {
  startRun,
  getRuns,
  getRun,
  cancelRun,
  getCandidates,
  accept,
  dismiss,
  restore,
};
