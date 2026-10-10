import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { reminderApiService } from "@/api/reminderApiService";
import { RootState } from "../store";

interface ReminderState {
  /** Number of reminders delivered in-app that the user hasn't seen yet */
  unreadCount: number;
}

const initialState: ReminderState = {
  unreadCount: 0,
};

export const fetchUnreadReminderCount = createAsyncThunk("reminders/fetchUnreadCount", () =>
  reminderApiService.getUnreadCount(),
);

export const markRemindersRead = createAsyncThunk("reminders/markRead", () =>
  reminderApiService.markAllRead(),
);

const reminderSlice = createSlice({
  name: "reminders",
  initialState,
  reducers: {
    setUnreadReminderCount(state, action: PayloadAction<number>) {
      state.unreadCount = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUnreadReminderCount.fulfilled, (state, action) => {
        state.unreadCount = action.payload;
      })
      // Clear optimistically so the bubble disappears as soon as the page opens
      .addCase(markRemindersRead.pending, (state) => {
        state.unreadCount = 0;
      });
  },
});

export const { setUnreadReminderCount } = reminderSlice.actions;

export const selectUnreadReminderCount = (state: RootState) => state.reminders.unreadCount;

export default reminderSlice.reducer;
