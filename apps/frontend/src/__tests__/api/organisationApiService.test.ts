import { describe, it, expect, beforeEach, vi } from "vitest";
import { organisationApiService, OrganisationSearchResponse } from "@/api/organisationApiService";
import { mockFetchRequest, mockSendFormDataRequest, resetAllMocks } from "../mocks/fetchHelper";

describe("organisationApiService", () => {
  beforeEach(() => {
    resetAllMocks();
    vi.useRealTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("search", () => {
    it("should search for organisations by name", async () => {
      const mockResults: OrganisationSearchResponse[] = [
        {
          id: 1,
          name: "Festival de Jazz",
          country: "France",
          town: "Paris",
          type: "FESTIVAL",
        },
        {
          id: 2,
          name: "Jazz Fest International",
          country: "Germany",
          town: "Berlin",
          type: "FESTIVAL",
        },
      ];

      mockFetchRequest.mockResolvedValue(mockResults);

      const result = await organisationApiService.search("Jazz");

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result).toHaveLength(2);
      expect(result[0].name).toContain("Jazz");
    });

    it("should return empty array for short search query", async () => {
      const result = await organisationApiService.search("J");

      expect(result).toEqual([]);
      expect(mockFetchRequest).not.toHaveBeenCalled();
    });

    it("should return empty array for empty search query", async () => {
      const result = await organisationApiService.search("");

      expect(result).toEqual([]);
      expect(mockFetchRequest).not.toHaveBeenCalled();
    });

    it("should search with type filter", async () => {
      const mockResults: OrganisationSearchResponse[] = [
        {
          id: 3,
          name: "Downtown Venue",
          country: "USA",
          town: "New York",
          type: "VENUE",
        },
      ];

      mockFetchRequest.mockResolvedValue(mockResults);

      const result = await organisationApiService.search("Venue", "venue");

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result).toHaveLength(1);
      expect(result[0].type).toBe("VENUE");
    });

    it("should search with lowercase type filter", async () => {
      const mockResults: OrganisationSearchResponse[] = [
        {
          id: 4,
          name: "Artist Residency Center",
          country: "Spain",
          town: "Barcelona",
          type: "RESIDENCY",
        },
      ];

      mockFetchRequest.mockResolvedValue(mockResults);

      const result = await organisationApiService.search("Residency", "RESIDENCY");

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result).toHaveLength(1);
    });

    it("should handle search with special characters", async () => {
      const mockResults: OrganisationSearchResponse[] = [];

      mockFetchRequest.mockResolvedValue(mockResults);

      const result = await organisationApiService.search("Jazz & Classical");

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result).toEqual([]);
    });

    it("should handle search error gracefully", async () => {
      const error = new Error("Search failed");
      mockFetchRequest.mockRejectedValue(error);

      await expect(organisationApiService.search("Festival")).rejects.toThrow("Search failed");
    });

    it("should return multiple results", async () => {
      const mockResults: OrganisationSearchResponse[] = [
        {
          id: 1,
          name: "Festival One",
          country: "France",
          town: "Paris",
          type: "FESTIVAL",
        },
        {
          id: 2,
          name: "Festival Two",
          country: "Italy",
          town: "Rome",
          type: "FESTIVAL",
        },
        {
          id: 3,
          name: "Festival Three",
          country: "Spain",
          town: "Madrid",
          type: "FESTIVAL",
        },
      ];

      mockFetchRequest.mockResolvedValue(mockResults);

      const result = await organisationApiService.search("Festival");

      expect(result).toHaveLength(3);
    });
  });

  describe("upload", () => {
    it("should upload an excel file", async () => {
      const mockFile = new File(["content"], "organisations.xlsx", {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      const mockTaskId = "task-123";

      mockSendFormDataRequest.mockResolvedValue({ taskId: mockTaskId });

      const result = await organisationApiService.upload([mockFile]);

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect(result).toBe(mockTaskId);
    });

    it("should upload multiple files", async () => {
      const mockFile1 = new File(["content1"], "organisations1.xlsx", {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const mockFile2 = new File(["content2"], "organisations2.xlsx", {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      const mockTaskId = "task-456";

      mockSendFormDataRequest.mockResolvedValue({ taskId: mockTaskId });

      const result = await organisationApiService.upload([mockFile1, mockFile2]);

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect(result).toBe(mockTaskId);
    });

    it("should handle upload error", async () => {
      const mockFile = new File(["content"], "organisations.xlsx", {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      const error = new Error("Upload failed");
      mockSendFormDataRequest.mockRejectedValue(error);

      await expect(organisationApiService.upload([mockFile])).rejects.toThrow("Upload failed");
    });

    it("should return task ID for tracking", async () => {
      const mockFile = new File(["content"], "orgs.xlsx", {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      const mockTaskId = "task-uuid-789";

      mockSendFormDataRequest.mockResolvedValue({ taskId: mockTaskId });

      const result = await organisationApiService.upload([mockFile]);

      expect(result).toBe(mockTaskId);
      expect(typeof result).toBe("string");
    });
  });

  describe("pollTask", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("should poll task until completion", async () => {
      const mockStats = {
        imported: 10,
        failed: 2,
        skipped: 1,
      };

      mockFetchRequest
        .mockResolvedValueOnce({
          status: "STARTED",
          stats: null,
        })
        .mockResolvedValueOnce({
          status: "STARTED",
          stats: null,
        })
        .mockResolvedValue({
          status: "SUCCESS",
          stats: mockStats,
        });

      const taskPromise = organisationApiService.pollTask("task-123");

      // Fast-forward through the polling intervals
      vi.advanceTimersByTime(2000); // First poll
      await Promise.resolve();
      vi.advanceTimersByTime(2000); // Second poll
      await Promise.resolve();
      vi.advanceTimersByTime(2000); // Third poll - should complete

      const result = await taskPromise;

      expect(result).toEqual(mockStats);
    });

    it("should handle task failure", async () => {
      mockFetchRequest.mockResolvedValue({
        status: "FAILURE",
        stats: null,
      });

      const taskPromise = organisationApiService.pollTask("task-failed");

      vi.advanceTimersByTime(2000);

      await expect(taskPromise).rejects.toThrow("Upload task failed");
    });

    it("should timeout after 5 minutes", async () => {
      mockFetchRequest.mockResolvedValue({
        status: "STARTED",
        stats: null,
      });

      const taskPromise = organisationApiService.pollTask("task-slow");

      // Advance time beyond the 5-minute timeout
      vi.advanceTimersByTime(5 * 60 * 1000 + 1000);

      await expect(taskPromise).rejects.toThrow("Upload task timeout");
    });

    it("should poll at 2-second intervals", async () => {
      const mockStats = {
        imported: 5,
        failed: 0,
        skipped: 0,
      };

      mockFetchRequest
        .mockResolvedValueOnce({
          status: "STARTED",
          stats: null,
        })
        .mockResolvedValue({
          status: "SUCCESS",
          stats: mockStats,
        });

      const taskPromise = organisationApiService.pollTask("task-interval");

      // First poll at 2 seconds
      vi.advanceTimersByTime(2000);
      await Promise.resolve();

      // Next poll at 2 seconds
      vi.advanceTimersByTime(2000);
      await Promise.resolve();

      const result = await taskPromise;

      expect(result).toEqual(mockStats);
      expect(mockFetchRequest).toHaveBeenCalledTimes(2);
    });

    it("should handle network error during polling", async () => {
      mockFetchRequest
        .mockResolvedValueOnce({
          status: "STARTED",
          stats: null,
        })
        .mockRejectedValue(new Error("Network error"));

      const taskPromise = organisationApiService.pollTask("task-network");

      vi.advanceTimersByTime(2000);
      await Promise.resolve();
      vi.advanceTimersByTime(2000);

      await expect(taskPromise).rejects.toThrow("Network error");
    });

    it("should return stats on pending status", async () => {
      const mockStats = {
        imported: 5,
        failed: 1,
        skipped: 0,
      };

      mockFetchRequest.mockResolvedValue({
        status: "PENDING",
        stats: mockStats,
      });

      // Pending status should keep polling, not complete
      const taskPromise = organisationApiService.pollTask("task-pending");

      vi.advanceTimersByTime(2000);
      await Promise.resolve();

      // After first poll, should still be polling (not resolved)
      expect(mockFetchRequest).toHaveBeenCalledTimes(1);

      // Continue polling for a few more intervals
      vi.advanceTimersByTime(2000);
      await Promise.resolve();
      vi.advanceTimersByTime(2000);
      await Promise.resolve();

      expect(mockFetchRequest).toHaveBeenCalledTimes(3);
    });
  });

  describe("Integration scenarios", () => {
    it("should search and get results with complete data", async () => {
      const mockResults: OrganisationSearchResponse[] = [
        {
          id: 100,
          name: "Grand International Festival",
          country: "France",
          town: "Cannes",
          type: "FESTIVAL",
        },
        {
          id: 101,
          name: "Local Festival",
          country: "France",
          town: "Lyon",
          type: "FESTIVAL",
        },
      ];

      mockFetchRequest.mockResolvedValue(mockResults);

      const results = await organisationApiService.search("Festival", "festival");

      expect(results).toHaveLength(2);
      expect(results[0].country).toBe("France");
      expect(results[1].town).toBe("Lyon");
    });

    it("should handle upload and poll workflow", async () => {
      const mockFile = new File(["xlsx content"], "bulk.xlsx");
      const mockTaskId = "upload-123";
      const mockStats = {
        imported: 50,
        failed: 2,
        skipped: 3,
      };

      // Mock upload
      mockSendFormDataRequest.mockResolvedValue({ taskId: mockTaskId });

      const uploadResult = await organisationApiService.upload([mockFile]);
      expect(uploadResult).toBe(mockTaskId);
      expect(typeof uploadResult).toBe("string");
    });
  });
});
