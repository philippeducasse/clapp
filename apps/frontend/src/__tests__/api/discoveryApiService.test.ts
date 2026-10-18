import { describe, it, expect, beforeEach } from "vitest";
import { discoveryApiService } from "@/api/discoveryApiService";
import {
  DiscoveryCandidateState,
  DiscoveryOrgType,
  DismissReason,
} from "@/interfaces/entities/Discovery";
import {
  mockFetchRequest,
  mockSendRequest,
  mockSilentRequest,
  resetAllMocks,
} from "../mocks/fetchHelper";

describe("discoveryApiService", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  it("starts a run from the starting point", async () => {
    mockSendRequest.mockResolvedValue({ id: 3, status: "QUEUED", isActive: true });

    const run = await discoveryApiService.startRun("https://some-juggler.com");

    expect(mockSendRequest).toHaveBeenCalledWith(
      "/api/discovery/runs",
      { startingPoint: "https://some-juggler.com" },
      "POST",
      "Discovery started",
    );
    expect(run.id).toBe(3);
  });

  it("propagates a refused start (e.g. 409, another run is active)", async () => {
    mockSendRequest.mockRejectedValue(new Error("Request failed: 409"));
    await expect(discoveryApiService.startRun("x")).rejects.toThrow("409");
  });

  it("lists recent runs", async () => {
    mockFetchRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });
    await discoveryApiService.getRuns();
    expect(mockFetchRequest).toHaveBeenCalledWith("/api/discovery/runs?limit=20");
  });

  it("polls a run without toasts", async () => {
    mockSilentRequest.mockResolvedValue({ id: 3, status: "RUNNING" });
    await discoveryApiService.getRun(3);
    expect(mockSilentRequest).toHaveBeenCalledWith("/api/discovery/runs/3");
    expect(mockFetchRequest).not.toHaveBeenCalled();
  });

  it("cancels a run", async () => {
    mockSendRequest.mockResolvedValue({ id: 3, cancelRequested: true });
    await discoveryApiService.cancelRun(3);
    expect(mockSendRequest).toHaveBeenCalledWith(
      "/api/discovery/runs/3/cancel",
      {},
      "POST",
      "Cancel requested",
    );
  });

  it("filters candidates by state and run", async () => {
    mockFetchRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });

    await discoveryApiService.getCandidates({ state: DiscoveryCandidateState.PENDING, run: 7 });
    expect(mockFetchRequest).toHaveBeenCalledWith(
      "/api/discovery/candidates?limit=200&state=PENDING&run=7",
    );

    await discoveryApiService.getCandidates();
    expect(mockFetchRequest).toHaveBeenLastCalledWith("/api/discovery/candidates?limit=200");
  });

  it("accepts with optional corrections", async () => {
    mockSendRequest.mockResolvedValue({ id: 5, state: "ACCEPTED" });

    await discoveryApiService.accept(5, { name: "Fest", orgType: DiscoveryOrgType.VENUE });
    expect(mockSendRequest).toHaveBeenCalledWith(
      "/api/discovery/candidates/5/accept",
      { name: "Fest", orgType: "VENUE" },
      "POST",
      "Added for all users",
    );

    await discoveryApiService.accept(6);
    expect(mockSendRequest).toHaveBeenLastCalledWith(
      "/api/discovery/candidates/6/accept",
      {},
      "POST",
      "Added for all users",
    );
  });

  it("dismisses with a reason and restores", async () => {
    mockSendRequest.mockResolvedValue({ id: 5 });

    await discoveryApiService.dismiss(5, DismissReason.WRONG_REGION);
    expect(mockSendRequest).toHaveBeenCalledWith(
      "/api/discovery/candidates/5/dismiss",
      { reason: "WRONG_REGION" },
      "POST",
      "Candidate dismissed",
    );

    await discoveryApiService.restore(5);
    expect(mockSendRequest).toHaveBeenLastCalledWith(
      "/api/discovery/candidates/5/restore",
      {},
      "POST",
      "Candidate restored",
    );
  });
});
