import { Reminder } from "@/interfaces/entities/Reminder";

export const RECENT_REMINDER_WINDOW_DAYS = 7;

export interface GroupedReminders {
  /** Not delivered yet, soonest first */
  upcoming: Reminder[];
  /** Delivered within the last 7 days, newest first */
  delivered: Reminder[];
  /** Delivered more than 7 days ago, newest first */
  past: Reminder[];
}

const time = (date: string) => new Date(date).getTime();

export const groupReminders = (reminders: Reminder[], now: Date = new Date()): GroupedReminders => {
  const cutoff = now.getTime() - RECENT_REMINDER_WINDOW_DAYS * 24 * 60 * 60 * 1000;
  const groups: GroupedReminders = { upcoming: [], delivered: [], past: [] };

  reminders.forEach((reminder) => {
    if (!reminder.deliveredAt) {
      groups.upcoming.push(reminder);
    } else if (time(reminder.deliveredAt) >= cutoff) {
      groups.delivered.push(reminder);
    } else {
      groups.past.push(reminder);
    }
  });

  groups.upcoming.sort((a, b) => time(a.remindAt) - time(b.remindAt));
  const newestFirst = (a: Reminder, b: Reminder) => time(b.deliveredAt!) - time(a.deliveredAt!);
  groups.delivered.sort(newestFirst);
  groups.past.sort(newestFirst);

  return groups;
};

export const isUnread = (reminder: Reminder): boolean => !!reminder.deliveredAt && !reminder.readAt;
