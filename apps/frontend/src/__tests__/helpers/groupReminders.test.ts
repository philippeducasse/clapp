import { describe, it, expect } from "vitest";
import {
  groupReminders,
  isUnread,
} from "@/components/page-components/reminders/helpers/groupReminders";
import { Reminder } from "@/interfaces/entities/Reminder";
import { OrganisationType } from "@/interfaces/Enums";

const NOW = new Date("2026-10-10T12:00:00Z");
const daysAgo = (days: number) => new Date(NOW.getTime() - days * 86_400_000).toISOString();
const daysAhead = (days: number) => daysAgo(-days);

const reminder = (id: number, overrides: Partial<Reminder> = {}): Reminder => ({
  id,
  objectId: 1,
  organisationType: OrganisationType.FESTIVAL,
  message: `Reminder ${id}`,
  remindAt: daysAhead(1),
  deliveredAt: null,
  readAt: null,
  ...overrides,
});

describe("groupReminders", () => {
  it("returns empty groups for no reminders", () => {
    expect(groupReminders([], NOW)).toEqual({ upcoming: [], delivered: [], past: [] });
  });

  it("splits reminders into upcoming, delivered (last 7 days) and past", () => {
    const upcoming = reminder(1);
    const delivered = reminder(2, { remindAt: daysAgo(2), deliveredAt: daysAgo(2) });
    const past = reminder(3, { remindAt: daysAgo(10), deliveredAt: daysAgo(10) });

    const groups = groupReminders([past, delivered, upcoming], NOW);

    expect(groups.upcoming.map((r) => r.id)).toEqual([1]);
    expect(groups.delivered.map((r) => r.id)).toEqual([2]);
    expect(groups.past.map((r) => r.id)).toEqual([3]);
  });

  it("keeps due but not yet delivered reminders in upcoming", () => {
    const due = reminder(1, { remindAt: daysAgo(0.01) });

    expect(groupReminders([due], NOW).upcoming).toEqual([due]);
  });

  it("treats a reminder delivered exactly 7 days ago as delivered", () => {
    const edge = reminder(1, { remindAt: daysAgo(7), deliveredAt: daysAgo(7) });

    expect(groupReminders([edge], NOW).delivered).toEqual([edge]);
  });

  it("sorts upcoming soonest first and delivered/past newest first", () => {
    const groups = groupReminders(
      [
        reminder(1, { remindAt: daysAhead(5) }),
        reminder(2, { remindAt: daysAhead(1) }),
        reminder(3, { deliveredAt: daysAgo(3) }),
        reminder(4, { deliveredAt: daysAgo(1) }),
        reminder(5, { deliveredAt: daysAgo(30) }),
        reminder(6, { deliveredAt: daysAgo(8) }),
      ],
      NOW,
    );

    expect(groups.upcoming.map((r) => r.id)).toEqual([2, 1]);
    expect(groups.delivered.map((r) => r.id)).toEqual([4, 3]);
    expect(groups.past.map((r) => r.id)).toEqual([6, 5]);
  });

  it("does not mutate the input array", () => {
    const input = [reminder(1, { remindAt: daysAhead(5) }), reminder(2)];
    groupReminders(input, NOW);
    expect(input.map((r) => r.id)).toEqual([1, 2]);
  });
});

describe("isUnread", () => {
  it("is true only for delivered reminders without readAt", () => {
    expect(isUnread(reminder(1, { deliveredAt: daysAgo(1) }))).toBe(true);
    expect(isUnread(reminder(2, { deliveredAt: daysAgo(1), readAt: daysAgo(0) }))).toBe(false);
    expect(isUnread(reminder(3))).toBe(false);
  });
});
