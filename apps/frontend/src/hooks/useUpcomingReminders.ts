"use client";
import { useEffect, useState } from "react";
import { reminderApiService } from "@/api/reminderApiService";
import { Reminder } from "@/interfaces/entities/Reminder";
import { OrganisationType } from "@/interfaces/Enums";

/**
 * Fetches the user's reminders once and returns the upcoming (not yet delivered)
 * ones for the given organisation type, keyed by organisation id and sorted soonest first.
 */
export const useUpcomingReminders = (
  organisationType: OrganisationType,
): Map<number, Reminder[]> => {
  const [remindersById, setRemindersById] = useState<Map<number, Reminder[]>>(new Map());

  useEffect(() => {
    let cancelled = false;
    reminderApiService
      .getReminders()
      .then((reminders) => {
        if (cancelled) return;
        const byId = new Map<number, Reminder[]>();
        reminders
          .filter((r) => r.organisationType === organisationType && !r.deliveredAt)
          .sort((a, b) => new Date(a.remindAt).getTime() - new Date(b.remindAt).getTime())
          .forEach((r) => byId.set(r.objectId, [...(byId.get(r.objectId) ?? []), r]));
        setRemindersById(byId);
      })
      .catch((error) => console.error("Failed to fetch reminders:", error));
    return () => {
      cancelled = true;
    };
  }, [organisationType]);

  return remindersById;
};
