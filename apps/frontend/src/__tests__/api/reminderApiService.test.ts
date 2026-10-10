import { describe, it, expect, beforeEach } from "vitest";
import { reminderApiService } from "@/api/reminderApiService";
import { OrganisationType } from "@/interfaces/Enums";
import {
  mockFetchRequest,
  mockSendRequest,
  mockDeleteRequest,
  mockSilentRequest,
  resetAllMocks,
} from "../mocks/fetchHelper";

describe("reminderApiService", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  it("getReminders fetches all reminders", async () => {
    mockFetchRequest.mockResolvedValue([]);

    await reminderApiService.getReminders();

    expect(mockFetchRequest).toHaveBeenCalledWith("/api/profiles/me/reminders");
  });

  it("getRemindersForEntity filters by organisation", async () => {
    mockFetchRequest.mockResolvedValue([]);

    await reminderApiService.getRemindersForEntity(OrganisationType.FESTIVAL, 3);

    expect(mockFetchRequest).toHaveBeenCalledWith(
      "/api/profiles/me/reminders?organisation_type=FESTIVAL&object_id=3",
    );
  });

  it("setReminder posts the reminder", async () => {
    const reminder = {
      organisationType: OrganisationType.VENUE,
      objectId: 1,
      message: "Apply",
      remindAt: "2026-12-01T10:00:00Z",
    };
    mockSendRequest.mockResolvedValue({ id: 1, ...reminder });

    await reminderApiService.setReminder(reminder);

    expect(mockSendRequest).toHaveBeenCalledWith(
      "/api/profiles/me/reminders",
      reminder,
      "POST",
      "Reminder successfully set",
    );
  });

  it("deleteReminder deletes by id", async () => {
    mockDeleteRequest.mockResolvedValue(undefined);

    await reminderApiService.deleteReminder(5);

    expect(mockDeleteRequest).toHaveBeenCalledWith(
      "/api/profiles/me/reminders/5",
      "Reminder successfully deleted",
    );
  });

  describe("getUnreadCount", () => {
    it("silently fetches and returns the unread count", async () => {
      mockSilentRequest.mockResolvedValue({ count: 4 });

      const count = await reminderApiService.getUnreadCount();

      expect(mockSilentRequest).toHaveBeenCalledWith("/api/profiles/me/reminders/unread-count");
      expect(count).toBe(4);
    });

    it("propagates errors", async () => {
      mockSilentRequest.mockRejectedValue(new Error("Network error"));

      await expect(reminderApiService.getUnreadCount()).rejects.toThrow("Network error");
    });
  });

  describe("markAllRead", () => {
    it("silently posts to mark-read and returns the number updated", async () => {
      mockSilentRequest.mockResolvedValue({ updated: 2 });

      const updated = await reminderApiService.markAllRead();

      expect(mockSilentRequest).toHaveBeenCalledWith(
        "/api/profiles/me/reminders/mark-read",
        "POST",
      );
      expect(updated).toBe(2);
    });

    it("propagates errors", async () => {
      mockSilentRequest.mockRejectedValue(new Error("403"));

      await expect(reminderApiService.markAllRead()).rejects.toThrow("403");
    });
  });
});
