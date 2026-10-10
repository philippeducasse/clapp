import { describe, it, expect, beforeEach } from "vitest";
import { configureStore } from "@reduxjs/toolkit";
import reminderReducer, {
  fetchUnreadReminderCount,
  markRemindersRead,
  selectUnreadReminderCount,
  setUnreadReminderCount,
} from "@/redux/slices/reminderSlice";
import { RootState } from "@/redux/store";
import { mockSilentRequest, resetAllMocks } from "../mocks/fetchHelper";

const makeStore = () => configureStore({ reducer: { reminders: reminderReducer } });

describe("Reminder Slice", () => {
  beforeEach(() => {
    resetAllMocks();
  });

  it("has an unread count of 0 initially", () => {
    const state = reminderReducer(undefined, { type: "unknown" });
    expect(state.unreadCount).toBe(0);
  });

  it("sets the unread count", () => {
    const state = reminderReducer(undefined, setUnreadReminderCount(3));
    expect(state.unreadCount).toBe(3);
  });

  it("selects the unread count", () => {
    const state = { reminders: { unreadCount: 7 } } as RootState;
    expect(selectUnreadReminderCount(state)).toBe(7);
  });

  it("fetchUnreadReminderCount stores the fetched count", async () => {
    mockSilentRequest.mockResolvedValue({ count: 5 });
    const store = makeStore();

    await store.dispatch(fetchUnreadReminderCount());

    expect(store.getState().reminders.unreadCount).toBe(5);
  });

  it("fetchUnreadReminderCount keeps the previous count on failure", async () => {
    mockSilentRequest.mockRejectedValue(new Error("Network error"));
    const store = makeStore();
    store.dispatch(setUnreadReminderCount(2));

    await store.dispatch(fetchUnreadReminderCount());

    expect(store.getState().reminders.unreadCount).toBe(2);
  });

  it("markRemindersRead clears the count immediately", async () => {
    let resolve: (value: { updated: number }) => void = () => {};
    mockSilentRequest.mockReturnValue(new Promise((r) => (resolve = r)));
    const store = makeStore();
    store.dispatch(setUnreadReminderCount(4));

    const pending = store.dispatch(markRemindersRead());
    expect(store.getState().reminders.unreadCount).toBe(0);

    resolve({ updated: 4 });
    await pending;
    expect(store.getState().reminders.unreadCount).toBe(0);
    expect(mockSilentRequest).toHaveBeenCalledWith("/api/profiles/me/reminders/mark-read", "POST");
  });
});
