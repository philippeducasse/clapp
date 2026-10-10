"use client";

import { useEffect } from "react";
import { useAppDispatch } from "@/redux/hook";
import { fetchUnreadReminderCount } from "@/redux/slices/reminderSlice";

export const REMINDER_POLL_INTERVAL_MS = 15 * 60 * 1000;

/**
 * Keeps the unread reminder count in Redux up to date: fetches on mount,
 * every 15 minutes, and whenever the tab becomes visible again.
 */
export default function ReminderPoller() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const refresh = () => {
      dispatch(fetchUnreadReminderCount());
    };
    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") refresh();
    };

    refresh();
    const interval = setInterval(refresh, REMINDER_POLL_INTERVAL_MS);
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [dispatch]);

  return null;
}
