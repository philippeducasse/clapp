import { describe, it, expect, beforeEach } from "vitest";
import { applicationApiService } from "@/api/applicationApiService";
import { Application, ApplicationMethod, ApplicationStatus } from "@/interfaces/entities/Application";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockPatchRequest,
  resetAllMocks,
} from "../mocks/fetchHelper";

describe("applicationApiService", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe("getAll", () => {
    it("should fetch all applications without params", async () => {
      const mockData: PaginatedResponse<Application> = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            organisation: { id: 1, name: "Festival 1" },
            organisationType: "Festival",
            profile: 1,
            applicationDate: "2025-01-15",
            applicationMethod: ApplicationMethod.EMAIL,
            status: ApplicationStatus.APPLIED,
            createdAt: "2025-01-15T10:00:00",
          },
          {
            id: 2,
            organisation: { id: 2, name: "Venue 1" },
            organisationType: "Venue",
            profile: 1,
            applicationDate: "2025-01-16",
            applicationMethod: ApplicationMethod.FORM,
            status: ApplicationStatus.DRAFT,
            createdAt: "2025-01-16T10:00:00",
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await applicationApiService.getAll();

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.count).toBe(2);
      expect(result.results).toHaveLength(2);
    });

    it("should fetch applications with pagination params", async () => {
      const mockData: PaginatedResponse<Application> = {
        count: 50,
        next: "http://api/applications/?offset=10",
        previous: null,
        results: [],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await applicationApiService.getAll({
        offset: 0,
        limit: 10,
      });

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.count).toBe(50);
    });

    it("should fetch applications with status filter", async () => {
      const mockData: PaginatedResponse<Application> = {
        count: 3,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            organisation: { id: 1, name: "Festival 1" },
            organisationType: "Festival",
            profile: 1,
            applicationDate: "2025-01-15",
            applicationMethod: ApplicationMethod.EMAIL,
            status: ApplicationStatus.APPLIED,
            createdAt: "2025-01-15T10:00:00",
          },
        ],
      };

      mockFetchRequest.mockResolvedValue(mockData);

      const result = await applicationApiService.getAll({
        filters: [{ column: "status", value: ApplicationStatus.APPLIED }],
      });

      expect(mockFetchRequest).toHaveBeenCalled();
      expect(result.results).toHaveLength(1);
      expect(result.results[0].status).toBe(ApplicationStatus.APPLIED);
    });
  });

  describe("get", () => {
    it("should fetch a single application by ID", async () => {
      const mockApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Application to Festival",
        message: "I would like to apply...",
        status: ApplicationStatus.APPLIED,
        createdAt: "2025-01-15T10:00:00",
        updatedAt: "2025-01-15T11:00:00",
      };

      mockFetchRequest.mockResolvedValue(mockApplication);

      const result = await applicationApiService.get(1);

      expect(mockFetchRequest).toHaveBeenCalledWith("/api/applications/1");
      expect(result.id).toBe(1);
      expect(result.status).toBe(ApplicationStatus.APPLIED);
    });

    it("should handle application not found", async () => {
      const error = new Error("Not found");
      mockFetchRequest.mockRejectedValue(error);

      await expect(applicationApiService.get(999)).rejects.toThrow("Not found");
    });
  });

  describe("create", () => {
    it("should create a new application", async () => {
      const newApplication: Application = {
        id: 3,
        organisation: { id: 3, name: "Festival 3" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-20",
        applicationMethod: ApplicationMethod.EMAIL,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-20T10:00:00",
      };

      mockSendRequest.mockResolvedValue(newApplication);

      const result = await applicationApiService.create(newApplication);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/applications",
        newApplication,
        "POST",
        "Application successfully created",
      );
      expect(result.id).toBe(3);
      expect(result.status).toBe(ApplicationStatus.DRAFT);
    });

    it("should create application with email details", async () => {
      const applicationWithEmail: Application = {
        id: 4,
        organisation: { id: 4, name: "Venue 4" },
        organisationType: "Venue",
        profile: 1,
        applicationDate: "2025-01-21",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Application",
        message: "I am interested...",
        emailRecipients: ["contact@venue.com"],
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-21T10:00:00",
      };

      mockSendRequest.mockResolvedValue(applicationWithEmail);

      const result = await applicationApiService.create(applicationWithEmail);

      expect(result.emailSubject).toBe("Application");
      expect(result.emailRecipients).toContain("contact@venue.com");
    });

    it("should create application with multiple attachments", async () => {
      const mockFiles = [new File(["content"], "resume.pdf", { type: "application/pdf" })];
      const applicationWithAttachments: Application = {
        id: 5,
        organisation: { id: 5, name: "Residency 5" },
        organisationType: "Residency",
        profile: 1,
        applicationDate: "2025-01-22",
        applicationMethod: ApplicationMethod.FORM,
        attachmentsSent: mockFiles,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-22T10:00:00",
      };

      mockSendRequest.mockResolvedValue(applicationWithAttachments);

      const result = await applicationApiService.create(applicationWithAttachments);

      expect(result.attachmentsSent).toBeDefined();
      expect(result.attachmentsSent).toHaveLength(1);
    });

    it("should handle creation error", async () => {
      const error = new Error("Validation error");
      mockSendRequest.mockRejectedValue(error);

      const application: Application = {
        id: 6,
        organisation: { id: 6, name: "Invalid" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-23",
        applicationMethod: ApplicationMethod.FORM,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-23T10:00:00",
      };

      await expect(applicationApiService.create(application)).rejects.toThrow("Validation error");
    });
  });

  describe("update", () => {
    it("should update an existing application", async () => {
      const updatedApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        message: "Updated application message",
        status: ApplicationStatus.APPLIED,
        comments: "Added comments",
        createdAt: "2025-01-15T10:00:00",
        updatedAt: "2025-01-20T15:30:00",
      };

      mockSendRequest.mockResolvedValue(updatedApplication);

      const result = await applicationApiService.update(updatedApplication);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/applications/1",
        updatedApplication,
        "PUT",
        "Application successfully updated",
      );
      expect(result.message).toBe("Updated application message");
      expect(result.comments).toBe("Added comments");
    });

    it("should update application status via PUT", async () => {
      const application: Application = {
        id: 2,
        organisation: { id: 2, name: "Venue 2" },
        organisationType: "Venue",
        profile: 1,
        applicationDate: "2025-01-16",
        applicationMethod: ApplicationMethod.FORM,
        status: ApplicationStatus.IN_DISCUSSION,
        createdAt: "2025-01-16T10:00:00",
      };

      mockSendRequest.mockResolvedValue(application);

      const result = await applicationApiService.update(application);

      expect(result.status).toBe(ApplicationStatus.IN_DISCUSSION);
    });

    it("should handle update error", async () => {
      const error = new Error("Not found");
      mockSendRequest.mockRejectedValue(error);

      const application: Application = {
        id: 999,
        organisation: { id: 999, name: "Non-existent" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-25",
        applicationMethod: ApplicationMethod.FORM,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-25T10:00:00",
      };

      await expect(applicationApiService.update(application)).rejects.toThrow("Not found");
    });
  });

  describe("remove", () => {
    it("should delete an application", async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await applicationApiService.remove(1);

      expect(mockDeleteRequest).toHaveBeenCalledWith(
        "/api/applications/1",
        "Application successfully deleted",
      );
    });

    it("should handle deletion error", async () => {
      const error = new Error("Not found");
      mockDeleteRequest.mockRejectedValue(error);

      await expect(applicationApiService.remove(999)).rejects.toThrow("Not found");
    });

    it("should delete multiple applications in sequence", async () => {
      mockDeleteRequest.mockResolvedValue(undefined);

      await applicationApiService.remove(1);
      await applicationApiService.remove(2);
      await applicationApiService.remove(3);

      expect(mockDeleteRequest).toHaveBeenCalledTimes(3);
    });
  });

  describe("changeStatus", () => {
    it("should change application status to APPLIED", async () => {
      const updatedApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        status: ApplicationStatus.APPLIED,
        createdAt: "2025-01-15T10:00:00",
        updatedAt: "2025-01-20T10:00:00",
      };

      mockPatchRequest.mockResolvedValue(updatedApplication);

      const result = await applicationApiService.changeStatus(1, ApplicationStatus.APPLIED);

      expect(mockPatchRequest).toHaveBeenCalledWith(
        "/api/applications/1/status/APPLIED",
        "Festival status successfully updated",
      );
      expect(result.status).toBe(ApplicationStatus.APPLIED);
    });

    it("should change application status to REJECTED", async () => {
      const rejectedApplication: Application = {
        id: 2,
        organisation: { id: 2, name: "Venue 2" },
        organisationType: "Venue",
        profile: 1,
        applicationDate: "2025-01-16",
        applicationMethod: ApplicationMethod.FORM,
        status: ApplicationStatus.REJECTED,
        createdAt: "2025-01-16T10:00:00",
        updatedAt: "2025-01-20T10:00:00",
      };

      mockPatchRequest.mockResolvedValue(rejectedApplication);

      const result = await applicationApiService.changeStatus(2, ApplicationStatus.REJECTED);

      expect(result.status).toBe(ApplicationStatus.REJECTED);
    });

    it("should change application status through all transitions", async () => {
      const statuses = [
        ApplicationStatus.DRAFT,
        ApplicationStatus.APPLIED,
        ApplicationStatus.IN_DISCUSSION,
        ApplicationStatus.ACCEPTED,
      ];

      for (const status of statuses) {
        mockPatchRequest.mockResolvedValue({
          id: 1,
          status,
          organisation: { id: 1, name: "Festival" },
          organisationType: "Festival",
          profile: 1,
          applicationDate: "2025-01-15",
          applicationMethod: ApplicationMethod.EMAIL,
          createdAt: "2025-01-15T10:00:00",
        });

        const result = await applicationApiService.changeStatus(1, status);
        expect(result.status).toBe(status);
      }

      expect(mockPatchRequest).toHaveBeenCalledTimes(4);
    });

    it("should handle status change error", async () => {
      const error = new Error("Invalid status transition");
      mockPatchRequest.mockRejectedValue(error);

      await expect(
        applicationApiService.changeStatus(999, ApplicationStatus.ACCEPTED),
      ).rejects.toThrow("Invalid status transition");
    });
  });

  describe("Edge cases and integration scenarios", () => {
    it("should handle application with all fields", async () => {
      const fullApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Full Festival" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Subject",
        message: "Message",
        emailRecipients: ["contact@festival.com"],
        attachmentsSent: [new File(["content"], "file.pdf")],
        status: ApplicationStatus.APPLIED,
        comments: "Comments",
        createdAt: "2025-01-15T10:00:00",
        updatedAt: "2025-01-20T10:00:00",
      };

      mockSendRequest.mockResolvedValue(fullApplication);

      const result = await applicationApiService.create(fullApplication);

      expect(result.emailSubject).toBeDefined();
      expect(result.message).toBeDefined();
      expect(result.comments).toBeDefined();
    });

    it("should handle application with minimal fields", async () => {
      const minimalApplication: Application = {
        id: 2,
        organisation: { id: 2, name: "Minimal Venue" },
        organisationType: "Venue",
        profile: 1,
        applicationDate: "2025-01-16",
        applicationMethod: ApplicationMethod.FORM,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-16T10:00:00",
      };

      mockSendRequest.mockResolvedValue(minimalApplication);

      const result = await applicationApiService.create(minimalApplication);

      expect(result.id).toBe(2);
      expect(result.organisationType).toBe("Venue");
    });

    it("should handle different application methods", async () => {
      const methods = [
        ApplicationMethod.EMAIL,
        ApplicationMethod.FORM,
        ApplicationMethod.INVITATION,
        ApplicationMethod.OTHER,
      ];

      for (const method of methods) {
        const app: Application = {
          id: 1,
          organisation: { id: 1, name: "Festival" },
          organisationType: "Festival",
          profile: 1,
          applicationDate: "2025-01-15",
          applicationMethod: method,
          status: ApplicationStatus.DRAFT,
          createdAt: "2025-01-15T10:00:00",
        };

        mockFetchRequest.mockResolvedValue(app);

        const result = await applicationApiService.get(1);
        expect(result.applicationMethod).toBe(method);
      }
    });

    it("should handle different organisation types", async () => {
      const types = ["Festival", "Venue", "Residency"];

      for (const type of types) {
        const app: Application = {
          id: 1,
          organisation: { id: 1, name: type },
          organisationType: type as "Festival" | "Venue" | "Residency",
          profile: 1,
          applicationDate: "2025-01-15",
          applicationMethod: ApplicationMethod.EMAIL,
          status: ApplicationStatus.DRAFT,
          createdAt: "2025-01-15T10:00:00",
        };

        mockFetchRequest.mockResolvedValue(app);

        const result = await applicationApiService.get(1);
        expect(result.organisationType).toBe(type);
      }
    });
  });
});
