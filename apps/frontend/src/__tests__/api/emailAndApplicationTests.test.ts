import { describe, it, expect, beforeEach } from "vitest";
import { festivalApiService } from "@/api/festivalApiService";
import { residencyApiService } from "@/api/residencyApiService";
import { venueApiService } from "@/api/venueApiService";
import {
  ApplicationCreate,
  ApplicationStatus,
  ApplicationMethod,
} from "@/interfaces/entities/Application";
import { Profile } from "@/interfaces/entities/Profile";
import { PerformanceType, PerformanceGenre } from "@/interfaces/entities/Performance";
import { mockSendRequest, mockSendFormDataRequest, resetAllMocks } from "../mocks/fetchHelper";

describe("Email and Application Functionality", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  describe("Festival Email Generation", () => {
    it("should generate email for festival with profile and performances", async () => {
      const mockProfile: Profile = {
        id: 1,
        email: "performer@example.com",
        firstName: "John",
        lastName: "Doe",
        companyName: "Circus Act Inc",
        confirmedAccount: true,
        performances: [],
      };

      const selectedPerformanceIds = [1, 2, 3];

      const mockResponse = {
        message: "Dear Jazz Festival,\n\nI am interested in performing at your festival...",
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await festivalApiService.generateEmail(1, {
        profile: mockProfile,
        selectedPerformanceIds,
      });

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/festivals/1/generate_email/",
        {
          profile: mockProfile,
          selectedPerformanceIds,
        },
        "POST",
        "Email successfully generated",
        true,
      );
      expect(result.message).toBeDefined();
      expect(result.message).toContain("Dear");
    });

    it("should generate email for festival without selected performances", async () => {
      const mockProfile: Profile = {
        id: 2,
        email: "artist@example.com",
        firstName: "Jane",
        lastName: "Smith",
        confirmedAccount: true,
        performances: [],
      };

      const mockResponse = {
        message: "Email template generated",
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await festivalApiService.generateEmail(5, {
        profile: mockProfile,
      });

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/festivals/5/generate_email/",
        {
          profile: mockProfile,
        },
        "POST",
        "Email successfully generated",
        true,
      );
      expect(result.message).toBeDefined();
    });

    it("should generate email with multiple performances", async () => {
      const mockProfile: Profile = {
        id: 1,
        email: "performer@example.com",
        confirmedAccount: true,
        performances: [],
      };

      const mockResponse = {
        message: "Generated email listing all performances",
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await festivalApiService.generateEmail(1, {
        profile: mockProfile,
        selectedPerformanceIds: [1, 2, 3, 4, 5],
      });

      expect(mockSendRequest).toHaveBeenCalled();
      expect(result.message).toBeDefined();
    });
  });

  describe("Residency Email Generation", () => {
    it("should generate email for residency", async () => {
      const mockResponse = {
        message: "Email generated for residency application",
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await residencyApiService.generateEmail(1);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/residencies/1/generate_email/",
        { message: "" },
        "POST",
        "Email successfully generated",
      );
      expect(result.message).toBeDefined();
    });

    it("should generate email for different residency IDs", async () => {
      mockSendRequest.mockResolvedValue({ message: "Email generated" });

      await residencyApiService.generateEmail(42);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/residencies/42/generate_email/",
        { message: "" },
        "POST",
        "Email successfully generated",
      );
    });
  });

  describe("Venue Email Generation", () => {
    it("should generate email for venue", async () => {
      const mockResponse = {
        message: "Email generated for venue booking",
      };

      mockSendRequest.mockResolvedValue(mockResponse);

      const result = await venueApiService.generateEmail(1);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/venues/1/generate_email/",
        { message: "" },
        "POST",
        "Email successfully generated",
      );
      expect(result.message).toBeDefined();
    });

    it("should generate email for different venue IDs", async () => {
      mockSendRequest.mockResolvedValue({ message: "Email generated" });

      await venueApiService.generateEmail(99);

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/venues/99/generate_email/",
        { message: "" },
        "POST",
        "Email successfully generated",
      );
    });
  });

  describe("Festival Application Submission", () => {
    it("should apply to festival with email method", async () => {
      const mockFile = new File(["content"], "performance_dossier.pdf", {
        type: "application/pdf",
      });

      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Application to Jazz Festival",
        message: "I would like to perform at your festival",
        status: ApplicationStatus.APPLIED,
      };

      const mockResponse = {
        message: "Application sent successfully",
        applicationId: 42,
      };

      mockSendFormDataRequest.mockResolvedValue(mockResponse);

      const result = await festivalApiService.apply(1, application, [mockFile], "dossier");

      expect(mockSendFormDataRequest).toHaveBeenCalledWith(
        "/api/festivals/1/apply/",
        expect.objectContaining({
          profileId: 1,
          emailSubject: "Application to Jazz Festival",
        }),
        [mockFile],
        "dossier",
        "POST",
        "Application successfully sent",
      );
      expect((result as { applicationId: number }).applicationId).toBe(42);
    });

    it("should apply to festival with multiple attachments", async () => {
      const file1 = new File(["dossier"], "dossier.pdf", { type: "application/pdf" });
      const file2 = new File(["photo"], "performance_photo.jpg", { type: "image/jpeg" });
      const file3 = new File(["video"], "performance_demo.mp4", { type: "video/mp4" });

      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Performance Application",
        message: "Please review my attached materials",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "All files uploaded successfully",
        applicationId: 43,
      });

      const result = await festivalApiService.apply(
        1,
        application,
        [file1, file2, file3],
        "attachments",
      );

      expect(mockSendFormDataRequest).toHaveBeenCalledWith(
        "/api/festivals/1/apply/",
        expect.any(Object),
        [file1, file2, file3],
        "attachments",
        "POST",
        "Application successfully sent",
      );
      expect((result as { applicationId: number }).applicationId).toBe(43);
    });

    it("should apply to festival without attachments", async () => {
      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 2,
        organisationType: "Festival",
        applicationDate: "2024-01-16",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Application",
        message: "Interested in performing",
        status: ApplicationStatus.APPLIED,
      };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Application sent",
        applicationId: 44,
      });

      const result = await festivalApiService.apply(2, application, [], "attachments");

      expect(mockSendFormDataRequest).toHaveBeenCalledWith(
        "/api/festivals/2/apply/",
        expect.any(Object),
        [],
        "attachments",
        "POST",
        "Application successfully sent",
      );
      expect((result as { applicationId: number }).applicationId).toBe(44);
    });

    it("should apply with selected performances in email", async () => {
      const mockFile = new File(["content"], "dossier.pdf");

      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        message: "Applying with specific performances",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Application with performances sent",
        applicationId: 45,
      });

      const result = await festivalApiService.apply(1, application, [mockFile], "attachments");

      expect((result as { applicationId: number }).applicationId).toBe(45);
    });
  });

  describe("Residency Application Submission", () => {
    it("should apply to residency with files", async () => {
      const mockFile = new File(["content"], "cv.pdf", { type: "application/pdf" });

      const application: ApplicationCreate = {
        profileId: 2,
        objectType: "Residency",
        objectId: 1,
        organisationType: "Residency",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Residency Application",
        message: "Applying for artistic residency",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Residency application sent",
        applicationId: 50,
      });

      const result = await residencyApiService.apply(1, application, [mockFile], "documents");

      expect(mockSendFormDataRequest).toHaveBeenCalledWith(
        "/api/residencies/1/apply/",
        expect.any(Object),
        [mockFile],
        "documents",
        "POST",
        "Application successfully sent",
      );
      expect((result as { applicationId: number }).applicationId).toBe(50);
    });

    it("should apply to residency without files", async () => {
      const application: ApplicationCreate = {
        profileId: 2,
        objectType: "Residency",
        objectId: 2,
        organisationType: "Residency",
        applicationDate: "2024-01-16",
        applicationMethod: ApplicationMethod.FORM,
        message: "Form-based application",
        status: ApplicationStatus.APPLIED,
      };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Residency application submitted",
        applicationId: 51,
      });

      await residencyApiService.apply(2, application, [], "attachments");

      expect(mockSendFormDataRequest).toHaveBeenCalledWith(
        "/api/residencies/2/apply/",
        expect.any(Object),
        [],
        "attachments",
        "POST",
        "Application successfully sent",
      );
    });
  });

  describe("Venue Application Submission", () => {
    it("should apply to venue with performance proposal", async () => {
      const mockFile = new File(["content"], "performance_proposal.pdf", {
        type: "application/pdf",
      });

      const application: ApplicationCreate = {
        profileId: 3,
        objectType: "Venue",
        objectId: 1,
        organisationType: "Venue",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Performance Booking Inquiry",
        message: "Interested in performing at your venue",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Booking inquiry sent",
        applicationId: 60,
      });

      const result = await venueApiService.apply(1, application, [mockFile], "proposal");

      expect(mockSendFormDataRequest).toHaveBeenCalledWith(
        "/api/venues/1/apply/",
        expect.any(Object),
        [mockFile],
        "proposal",
        "POST",
        "Application successfully sent",
      );
      expect(result).toBeDefined();
    });

    it("should apply to venue with multiple media files", async () => {
      const videoFile = new File(["video content"], "demo.mp4", { type: "video/mp4" });
      const photoFile = new File(["photo content"], "performer.jpg", { type: "image/jpeg" });

      const application: ApplicationCreate = {
        profileId: 3,
        objectType: "Venue",
        objectId: 2,
        organisationType: "Venue",
        applicationDate: "2024-01-16",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Street Performance at Your Venue",
        message: "See attached media of my performance",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Media files received",
        applicationId: 61,
      });

      const result = await venueApiService.apply(2, application, [videoFile, photoFile], "media");

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect(result).toBeDefined();
    });
  });

  describe("Email Application Edge Cases", () => {
    it("should handle application with custom email recipients", async () => {
      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Application with Custom Recipients",
        message: "Message",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Application sent to custom recipients",
        applicationId: 70,
      });

      const result = await festivalApiService.apply(1, application, [], "attachments");

      expect((result as { applicationId: number }).applicationId).toBe(70);
    });

    it("should handle large file uploads", async () => {
      const largeFile = new File(["x".repeat(10 * 1024 * 1024)], "large_video.mp4", {
        type: "video/mp4",
      });

      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        message: "Application with large file",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Large file processed",
        applicationId: 71,
      });

      const result = await festivalApiService.apply(1, application, [largeFile], "attachments");

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect((result as { applicationId: number }).applicationId).toBe(71);
    });

    it("should handle application with rich text message", async () => {
      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        emailSubject: "Application",
        message:
          "<p>Dear Festival Organizers,</p><p>I am a <b>professional performer</b> with <i>20 years</i> of experience...</p>",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Rich text message received",
        applicationId: 72,
      });

      const result = await festivalApiService.apply(1, application, [], "attachments");

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect((result as { applicationId: number }).applicationId).toBe(72);
    });

    it("should apply with FORM method instead of EMAIL", async () => {
      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.FORM,
        message: "Form submission",
        status: ApplicationStatus.APPLIED,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Form application received",
        applicationId: 73,
      });

      const result = await festivalApiService.apply(1, application, [], "attachments");

      expect(mockSendFormDataRequest).toHaveBeenCalled();
      expect((result as { applicationId: number }).applicationId).toBe(73);
    });

    it("should handle application DRAFT status", async () => {
      const application: ApplicationCreate = {
        profileId: 1,
        objectType: "Festival",
        objectId: 1,
        organisationType: "Festival",
        applicationDate: "2024-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        message: "Draft application",
        status: ApplicationStatus.DRAFT,
              };

      mockSendFormDataRequest.mockResolvedValue({
        message: "Draft saved",
        applicationId: 74,
      });

      const result = await festivalApiService.apply(1, application, [], "attachments");

      expect((result as { applicationId: number }).applicationId).toBe(74);
    });
  });

  describe("Email Generation with Profile Details", () => {
    it("should generate email including all profile information", async () => {
      const comprehensiveProfile: Profile = {
        id: 1,
        email: "comprehensive@example.com",
        firstName: "Alice",
        lastName: "Johnson",
        companyName: "Performance Arts Collective",
        personalWebsite: "https://alicejohnson.com",
        location: "Berlin, Germany",
        nationality: "British",
        spokenLanguages: ["English", "German", "French"],
        instagramProfile: "@alicejohnson",
        facebookProfile: "alicejohnson",
        confirmedAccount: true,
        performances: [
          {
            id: 1,
            profile: 1,
            performanceTitle: "Fire Dance",
            performanceType: PerformanceType.FIRE_SHOW,
            genres: [PerformanceGenre.FIRE_SHOW, PerformanceGenre.DANCE],
          },
        ],
      };

      mockSendRequest.mockResolvedValue({
        message: "Comprehensive email generated with full profile",
      });

      const result = await festivalApiService.generateEmail(1, {
        profile: comprehensiveProfile,
        selectedPerformanceIds: [1],
      });

      expect(mockSendRequest).toHaveBeenCalledWith(
        "/api/festivals/1/generate_email/",
        expect.objectContaining({
          profile: comprehensiveProfile,
          selectedPerformanceIds: [1],
        }),
        "POST",
        "Email successfully generated",
        true,
      );
      expect(result.message).toBeDefined();
    });

    it("should generate email with only basic profile information", async () => {
      const minimalProfile: Profile = {
        id: 99,
        email: "minimal@example.com",
        confirmedAccount: true,
        performances: [],
      };

      mockSendRequest.mockResolvedValue({
        message: "Basic email template generated",
      });

      const result = await festivalApiService.generateEmail(5, {
        profile: minimalProfile,
      });

      expect(mockSendRequest).toHaveBeenCalled();
      expect(result.message).toBeDefined();
    });
  });
});
