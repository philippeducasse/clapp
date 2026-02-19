import { describe, it, expect, beforeEach } from "vitest";
import { performanceApiService } from "@/api/performanceApiService";
import {
  Performance,
  PerformanceType,
  PerformanceGenre,
  Dossier,
} from "@/interfaces/entities/Performance";
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockSendFormDataRequest,
  resetAllMocks,
} from "../mocks/fetchHelper";

describe("performanceApiService", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe("getAll", () => {
    it("should fetch all performances for a user", async () => {
      const mockPerformances: Performance[] = [
        {
          id: 1,
          profile: 1,
          performanceTitle: "Juggling Act",
          shortDescription: "Amazing juggling performance",
          performanceType: PerformanceType.STREET,
          genres: [PerformanceGenre.JUGGLING],
        },
        {
          id: 2,
          profile: 1,
          performanceTitle: "Fire Show",
          shortDescription: "Spectacular fire performance",
          performanceType: PerformanceType.OUTDOOR,
          genres: [PerformanceGenre.FIRE_SHOW],
        },
      ];

      mockFetchRequest.mockResolvedValue(mockPerformances);

      const result = await performanceApiService.getAll(1);

      expect(mockFetchRequest).toHaveBeenCalledWith("/api/performances/1");
      expect(result).toHaveLength(2);
      expect(result[0].performanceTitle).toBe("Juggling Act");
    });

    it("should handle empty performance list", async () => {
      mockFetchRequest.mockResolvedValue([]);

      const result = await performanceApiService.getAll(99);

      expect(result).toHaveLength(0);
    });

    it("should fetch performances for different user IDs", async () => {
      mockFetchRequest.mockResolvedValue([]);

      await performanceApiService.getAll(42);

      expect(mockFetchRequest).toHaveBeenCalledWith("/api/performances/42");
    });
  });

  describe("get", () => {
    it("should fetch a single performance", async () => {
      const mockPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Juggling Act",
        shortDescription: "Amazing juggling performance",
        longDescription: "A detailed description of the juggling act",
        performanceType: PerformanceType.STREET,
        genres: [PerformanceGenre.JUGGLING],
        length: "30 minutes",
      };

      mockFetchRequest.mockResolvedValue(mockPerformance);

      const result = await performanceApiService.get(1);

      expect(mockFetchRequest).toHaveBeenCalledWith("/api/performances/1");
      expect(result.performanceTitle).toBe("Juggling Act");
      expect(result.performanceType).toBe(PerformanceType.STREET);
    });

    it("should fetch performance with multiple genres", async () => {
      const mockPerformance: Performance = {
        id: 2,
        profile: 1,
        performanceTitle: "Circus Act",
        genres: [PerformanceGenre.CIRCUS, PerformanceGenre.MUSIC, PerformanceGenre.DANCE],
        performanceType: PerformanceType.INDOOR_STAGE,
      };

      mockFetchRequest.mockResolvedValue(mockPerformance);

      const result = await performanceApiService.get(2);

      expect(result.genres).toEqual([
        PerformanceGenre.CIRCUS,
        PerformanceGenre.MUSIC,
        PerformanceGenre.DANCE,
      ]);
    });

    it("should fetch performance with dossiers", async () => {
      const mockDossier: Dossier = {
        id: 1,
        file: "https://example.com/dossier.pdf",
        uploadedAt: new Date("2024-01-15"),
        name: "Performance Dossier",
      };

      const mockPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Performance with Dossier",
        dossiers: [mockDossier],
      };

      mockFetchRequest.mockResolvedValue(mockPerformance);

      const result = await performanceApiService.get(1);

      expect(result.dossiers).toHaveLength(1);
      expect(result.dossiers?.[0].name).toBe("Performance Dossier");
    });
  });

  describe("create", () => {
    it("should create performance without files", async () => {
      const newPerformance: Performance = {
        id: 3,
        profile: 1,
        performanceTitle: "New Performance",
        shortDescription: "A new performance",
        performanceType: PerformanceType.INDOOR_STAGE,
        genres: [PerformanceGenre.CIRCUS],
      };

      const mockResponse: Performance = {
        ...newPerformance,
        id: 3,
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await performanceApiService.create(newPerformance);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/performances",
        expect.objectContaining({
          profile: 1,
          performanceTitle: "New Performance",
        }),
        "POST",
        "Performance successfully created",
        true,
      );
      expect(result.id).toBe(3);
    });

    it("should create performance with dossier files", async () => {
      const mockFile = new File(["content"], "dossier.pdf", { type: "application/pdf" });

      const newPerformance: Performance & { dossierFiles?: File[] } = {
        id: 4,
        profile: 1,
        performanceTitle: "Performance with Files",
        performanceType: PerformanceType.OUTDOOR,
        dossierFiles: [mockFile],
      };

      const mockResponse: Performance = {
        id: 4,
        profile: 1,
        performanceTitle: "Performance with Files",
        performanceType: PerformanceType.OUTDOOR,
        dossiers: [
          {
            id: 1,
            file: "https://example.com/dossier.pdf",
            uploadedAt: new Date(),
            name: "dossier.pdf",
          },
        ],
      };

      mockSendFormDataRequest.mockResolvedValue(mockResponse);

      const result = await performanceApiService.create(newPerformance);

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect(result.dossiers).toBeDefined();
    });

    it("should ignore empty dossier files array", async () => {
      const newPerformance: Performance & { dossierFiles?: File[] } = {
        id: 5,
        profile: 1,
        performanceTitle: "Performance without Files",
        dossierFiles: [],
      };

      mockSendRequest.mockResolvedValue(newPerformance);

      await performanceApiService.create(newPerformance);

      expect(mockSendRequest).toHaveBeenCalled();
      expect(mockSendFormDataRequest).not.toHaveBeenCalled();
    });
  });

  describe("update", () => {
    it("should update performance without dossiers", async () => {
      const updatedPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Updated Performance",
        shortDescription: "Updated description",
        performanceType: PerformanceType.INDOOR_STAGE,
      };

      const mockResponse: Performance = {
        ...updatedPerformance,
        dossiers: [],
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await performanceApiService.update(updatedPerformance);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/performances/1",
        expect.objectContaining({
          performanceTitle: "Updated Performance",
          dossierIds: [],
        }),
        "PUT",
        "Performance successfully updated",
        true,
      );
      expect(result.performanceTitle).toBe("Updated Performance");
    });

    it("should update performance with new files only", async () => {
      const mockFile = new File(["new content"], "new_dossier.pdf", { type: "application/pdf" });

      const updatedPerformance: Performance & {
        dossierFiles?: (File | { id: number; file: string; uploadedAt: Date | string })[];
      } = {
        id: 1,
        profile: 1,
        performanceTitle: "Updated with New Files",
        dossierFiles: [mockFile],
      };

      const mockResponse: Performance = {
        ...updatedPerformance,
        dossiers: [
          {
            id: 2,
            file: "https://example.com/new_dossier.pdf",
            uploadedAt: new Date(),
            name: "new_dossier.pdf",
          },
        ],
      };

      mockSendFormDataRequest.mockResolvedValue(mockResponse);

      const result = await performanceApiService.update(updatedPerformance);

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect(result.dossiers).toBeDefined();
    });

    it("should update performance keeping existing dossiers", async () => {
      const existingDossier = {
        id: 1,
        file: "https://example.com/old.pdf",
        uploadedAt: "2024-01-01",
      };

      const updatedPerformance: Performance & {
        dossierFiles?: (File | { id: number; file: string; uploadedAt: Date | string })[];
      } = {
        id: 1,
        profile: 1,
        performanceTitle: "Keep Dossiers",
        dossierFiles: [existingDossier],
      };

      mockSendRequest.mockResolvedValue(updatedPerformance);

      await performanceApiService.update(updatedPerformance);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/performances/1",
        expect.objectContaining({
          dossierIds: [1],
        }),
        "PUT",
        "Performance successfully updated",
        true,
      );
    });

    it("should handle mixed existing and new files", async () => {
      const existingDossier = {
        id: 1,
        file: "https://example.com/old.pdf",
        uploadedAt: "2024-01-01",
      };
      const newFile = new File(["new"], "new.pdf", { type: "application/pdf" });

      const updatedPerformance: Performance & {
        dossierFiles?: (File | { id: number; file: string; uploadedAt: Date | string })[];
      } = {
        id: 1,
        profile: 1,
        performanceTitle: "Mixed Files",
        dossierFiles: [existingDossier, newFile],
      };

      mockSendFormDataRequest.mockResolvedValue({
        ...updatedPerformance,
        dossiers: [
          { ...existingDossier, uploadedAt: new Date(existingDossier.uploadedAt) },
          { id: 2, file: "https://example.com/new.pdf", uploadedAt: new Date(), name: "new.pdf" },
        ],
      });

      await performanceApiService.update(updatedPerformance);

      expect(mockSendFormDataRequest).toHaveBeenCalled();
    });
  });

  describe("remove", () => {
    it("should delete performance", async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await performanceApiService.remove(1);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        "/api/performances/1",
        "Performance successfully deleted",
        true,
      );
    });

    it("should handle deletion of different performance IDs", async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await performanceApiService.remove(99);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        "/api/performances/99",
        "Performance successfully deleted",
        true,
      );
    });
  });

  describe("Complex scenarios", () => {
    it("should handle performance with all optional fields", async () => {
      const mockPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Comprehensive Performance",
        shortDescription: "A short description",
        longDescription: "A very detailed long description",
        trailer: "https://youtube.com/watch?v=xyz",
        length: "45 minutes",
        creationDate: new Date("2024-01-01"),
        performanceType: PerformanceType.FIRE_SHOW,
        genres: [PerformanceGenre.FIRE_SHOW, PerformanceGenre.MUSIC],
        dossiers: [
          {
            id: 1,
            file: "https://example.com/dossier1.pdf",
            uploadedAt: new Date("2024-01-15"),
            name: "Main Dossier",
          },
          {
            id: 2,
            file: "https://example.com/dossier2.pdf",
            uploadedAt: new Date("2024-02-01"),
            name: "Promotional Material",
          },
        ],
        emailPrompt: "This is a great performance!",
      };

      mockFetchRequest.mockResolvedValue(mockPerformance);

      const result = await performanceApiService.get(1);

      expect(result.dossiers).toHaveLength(2);
      expect(result.genres).toHaveLength(2);
      expect(result.trailer).toBe("https://youtube.com/watch?v=xyz");
    });

    it("should handle profile reference as number or object", async () => {
      const performanceWithProfileNumber: Performance = {
        id: 1,
        profile: 42,
        performanceTitle: "Performance with Profile ID",
      };

      const performanceWithProfileObject: Performance = {
        id: 2,
        profile: { id: 42, email: "user@example.com", confirmedAccount: true, performances: [] },
        performanceTitle: "Performance with Profile Object",
      };

      mockSendRequest
        .mockResolvedValueOnce(performanceWithProfileNumber)
        .mockResolvedValueOnce(performanceWithProfileObject);

      const result1 = await performanceApiService.create(performanceWithProfileNumber);
      const result2 = await performanceApiService.create(performanceWithProfileObject);

      expect(result1.profile).toBe(42);
      expect(typeof result2.profile).not.toBe("number");
    });
  });
});
