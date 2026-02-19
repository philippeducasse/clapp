import { describe, it, expect, beforeEach } from "vitest";
import { festivalApiService } from "@/api/festivalApiService";
import { Festival, FestivalType } from "@/interfaces/entities/Festival";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockPatchRequest,
  resetAllMocks,
} from "../mocks/fetchHelper";

describe("festivalApiService", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe("getAll", () => {
    it("should fetch all festivals without params", async () => {
      const mockData: PaginatedResponse<Festival> = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            name: "Jazz Festival",
            country: "France",
            town: "Paris",
            festivalType: FestivalType.MUSIC,
          },
          {
            id: 2,
            name: "Circus Festival",
            country: "Germany",
            town: "Berlin",
            festivalType: FestivalType.CIRCUS,
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await festivalApiService.getAll();

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result).toEqual(mockData);
    });

    it("should fetch festivals with pagination params", async () => {
      const mockData: PaginatedResponse<Festival> = {
        count: 100,
        next: "http://api/festivals/?offset=10",
        previous: null,
        results: [],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await festivalApiService.getAll({
        offset: 0,
        limit: 10,
      });

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.count).toBe(100);
    });

    it("should fetch festivals with search filter", async () => {
      const mockData: PaginatedResponse<Festival> = {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            name: "Jazz Festival",
            country: "France",
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await festivalApiService.getAll({
        search: "Jazz",
      });

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.results).toHaveLength(1);
    });
  });

  describe("get", () => {
    it("should fetch a single festival by ID", async () => {
      const mockFestival: Festival = {
        id: 1,
        name: "Jazz Festival",
        country: "France",
        town: "Paris",
        festivalType: FestivalType.MUSIC,
        websiteUrl: "https://example.com",
        contacts: [],
      };

      mockFetchRequest.mockResolvedValue(mockFestival);

      const result = await festivalApiService.get(1);

      expect(mockFetchRequest).toHaveBeenCalledWith("/api/festivals/1");
      expect(result).toEqual(mockFestival);
    });

    it("should handle festival not found", async () => {
      const error = new Error("Not found");
      mockFetchRequest.mockRejectedValue(error);

      await expect(festivalApiService.get(999)).rejects.toThrow("Not found");
    });
  });

  describe("create", () => {
    it("should create a new festival", async () => {
      const newFestival: Festival = {
        id: 3,
        name: "New Festival",
        country: "Spain",
        town: "Madrid",
        festivalType: FestivalType.OTHER,
      };

      mockSendRequest.mockResolvedValue(newFestival);

      const result = await festivalApiService.create(newFestival);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/festivals",
        newFestival,
        "POST",
        "Festival successfully created",
        true,
      );
      expect(result).toEqual(newFestival);
    });

    it("should create festival with contacts", async () => {
      const festivalWithContacts: Festival = {
        id: 4,
        name: "Festival with Contacts",
        country: "Italy",
        contacts: [
          {
            id: 1,
            email: "contact@festival.com",
            firstName: "John",
            lastName: "Doe",
          },
        ],
      };

      mockSendRequest.mockResolvedValue(festivalWithContacts);

      const result = await festivalApiService.create(festivalWithContacts);

      expect(result.contacts).toHaveLength(1);
      expect(result.contacts?.[0].email).toBe("contact@festival.com");
    });

    it("should handle creation error", async () => {
      const error = new Error("Validation error");
      mockSendRequest.mockRejectedValue(error);

      const festival: Festival = { id: 5, name: "Invalid Festival" };

      await expect(festivalApiService.create(festival)).rejects.toThrow("Validation error");
    });
  });

  describe("update", () => {
    it("should update an existing festival", async () => {
      const updatedFestival: Festival = {
        id: 1,
        name: "Updated Jazz Festival",
        country: "France",
        town: "Paris",
        festivalType: FestivalType.MUSIC,
      };

      mockSendRequest.mockResolvedValue(updatedFestival);

      const result = await festivalApiService.update(updatedFestival);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/festivals/1",
        updatedFestival,
        "PUT",
        "Festival successfully updated",
        true,
      );
      expect(result.name).toBe("Updated Jazz Festival");
    });

    it("should update festival type", async () => {
      const festival: Festival = {
        id: 2,
        name: "Circus Festival",
        festivalType: FestivalType.STREET,
      };

      mockSendRequest.mockResolvedValue(festival);

      const result = await festivalApiService.update(festival);

      expect(result.festivalType).toBe(FestivalType.STREET);
    });

    it("should handle update error", async () => {
      const error = new Error("Not found");
      mockSendRequest.mockRejectedValue(error);

      const festival: Festival = { id: 999, name: "Non-existent" };

      await expect(festivalApiService.update(festival)).rejects.toThrow("Not found");
    });
  });

  describe("remove", () => {
    it("should delete a festival", async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await festivalApiService.remove(1);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        "/api/festivals/1",
        "Festival successfully deleted",
        true,
      );
    });

    it("should handle deletion error", async () => {
      const error = new Error("Not found");
      mockDeleteRequest.mockRejectedValue(error);

      await expect(festivalApiService.remove(999)).rejects.toThrow("Not found");
    });

    it("should delete multiple festivals in sequence", async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await festivalApiService.remove(1);
      await festivalApiService.remove(2);
      await festivalApiService.remove(3);

      expect(mockDeleteRequest).toHaveBeenCalledTimes(3);
    });
  });

  describe("tag", () => {
    it("should tag a festival with STAR action", async () => {
      const taggedFestival: Festival = {
        id: 1,
        name: "Jazz Festival",
        tag: "STAR",
      };

      mockPatchRequest.mockResolvedValue(taggedFestival);

      const result = await festivalApiService.tag(1, TagAction.STAR);

      expect(mockPatchRequest).toHaveBeenCalledWith(
        "/api/festivals/1/tag/STAR",
        "Festival successfully tagged",
      );
      expect(result.tag).toBe("STAR");
    });

    it("should tag a festival with WATCH action", async () => {
      const taggedFestival: Festival = {
        id: 2,
        name: "Circus Festival",
        tag: "WATCH",
      };

      mockPatchRequest.mockResolvedValue(taggedFestival);

      const result = await festivalApiService.tag(2, TagAction.WATCH);

      expect(result.tag).toBe("WATCH");
    });
  });

  describe("enrich", () => {
    it("should enrich a festival with additional data", async () => {
      const enrichedFestival: Festival = {
        id: 1,
        name: "Jazz Festival",
        country: "France",
        town: "Paris",
        description: "A wonderful jazz festival",
        contacts: [],
      };

      mockFetchRequest.mockResolvedValue(enrichedFestival);

      const result = await festivalApiService.enrich(1);

      expect(mockFetchRequest).toHaveBeenCalledWith("/api/festivals/1/enrich");
      expect(result.description).toBeDefined();
    });
  });

  describe("Edge cases and integration scenarios", () => {
    it("should handle festival with all optional fields", async () => {
      const fullFestival: Festival = {
        id: 1,
        name: "Complete Festival",
        websiteUrl: "https://festival.com",
        country: "France",
        town: "Paris",
        approximateDate: "2025-07-15",
        startDate: new Date("2025-07-01"),
        endDate: new Date("2025-07-31"),
        festivalType: FestivalType.CIRCUS,
        applicationType: "FORM",
        applicationStart: "2025-01-01",
        applicationEnd: "2025-06-01",
        applied: true,
        description: "Amazing circus festival",
        tag: "STAR",
        comments: "Great opportunity",
        contacts: [
          {
            id: 1,
            email: "contact@festival.com",
            firstName: "Jane",
            lastName: "Smith",
          },
        ],
      };

      mockSendRequest.mockResolvedValue(fullFestival);

      const result = await festivalApiService.create(fullFestival);

      expect(result.websiteUrl).toBe("https://festival.com");
      expect(result.contacts).toHaveLength(1);
      expect(result.applied).toBe(true);
    });

    it("should handle festival with minimal fields", async () => {
      const minimalFestival: Festival = {
        id: 2,
        name: "Minimal Festival",
      };

      mockSendRequest.mockResolvedValue(minimalFestival);

      const result = await festivalApiService.create(minimalFestival);

      expect(result.id).toBe(2);
      expect(result.name).toBe("Minimal Festival");
    });
  });
});
