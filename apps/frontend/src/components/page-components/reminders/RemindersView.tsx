"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AlarmClock, BellRing, CalendarClock, History } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { reminderApiService } from "@/api/reminderApiService";
import { Reminder } from "@/interfaces/entities/Reminder";
import { useAppDispatch } from "@/redux/hook";
import { markRemindersRead } from "@/redux/slices/reminderSlice";
import ReminderItem from "./components/ReminderItem";
import {
  groupReminders,
  isUnread,
  RECENT_REMINDER_WINDOW_DAYS,
} from "./helpers/groupReminders";

interface ReminderSectionProps {
  title: string;
  icon: React.ReactNode;
  emptyText: string;
  reminders: Reminder[];
  isLoading: boolean;
  newIds?: Set<number>;
  onDelete?: (id: number) => void;
}

const ReminderSection = ({
  title,
  icon,
  emptyText,
  reminders,
  isLoading,
  newIds,
  onDelete,
}: ReminderSectionProps) => (
  <Card>
    <CardHeader>
      <CardTitle className="text-xl flex items-center gap-2">
        {icon} {title} {!isLoading && `(${reminders.length})`}
      </CardTitle>
    </CardHeader>
    <CardContent>
      {isLoading ? (
        <Skeleton className="h-6 w-full" />
      ) : reminders.length === 0 ? (
        <p className="text-muted-foreground text-sm italic">{emptyText}</p>
      ) : (
        <div className="space-y-3">
          {reminders.map((reminder) => (
            <ReminderItem
              key={reminder.id}
              reminder={reminder}
              isNew={newIds?.has(reminder.id)}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </CardContent>
  </Card>
);

const RemindersView = () => {
  const dispatch = useAppDispatch();
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showPast, setShowPast] = useState(false);
  // Reminders that were unread when the page was opened stay highlighted
  const [newIds, setNewIds] = useState<Set<number>>(new Set());
  const hasFetchedRef = useRef(false);

  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    reminderApiService
      .getReminders()
      .then((data) => {
        setReminders(data);
        const unread = data.filter(isUnread);
        setNewIds(new Set(unread.map((r) => r.id)));
        if (unread.length > 0) {
          dispatch(markRemindersRead());
        }
      })
      .catch((error) => console.error("Failed to fetch reminders:", error))
      .finally(() => setIsLoading(false));
  }, [dispatch]);

  const { upcoming, delivered, past } = useMemo(() => groupReminders(reminders), [reminders]);

  const handleDelete = async (reminderId: number) => {
    try {
      await reminderApiService.deleteReminder(reminderId);
      setReminders((prev) => prev.filter((r) => r.id !== reminderId));
    } catch (error) {
      console.error("Failed to delete reminder:", error);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl text-primary flex items-center gap-2">
            <AlarmClock /> Reminders
          </CardTitle>
          <CardDescription className="text-xl">
            Reminders appear here as soon as they are due, at the same time as the reminder email.
          </CardDescription>
        </CardHeader>
      </Card>

      <ReminderSection
        title="Delivered"
        icon={<BellRing className="text-primary" size={20} />}
        emptyText={`No reminders delivered in the last ${RECENT_REMINDER_WINDOW_DAYS} days`}
        reminders={delivered}
        isLoading={isLoading}
        newIds={newIds}
      />

      <ReminderSection
        title="Upcoming"
        icon={<CalendarClock className="text-primary" size={20} />}
        emptyText="No upcoming reminders"
        reminders={upcoming}
        isLoading={isLoading}
        onDelete={handleDelete}
      />

      {!isLoading && (
        <div className="flex justify-center">
          <Button variant="outline" onClick={() => setShowPast((prev) => !prev)}>
            <History />
            {showPast ? "Hide past reminders" : `Show past reminders (${past.length})`}
          </Button>
        </div>
      )}

      {showPast && (
        <ReminderSection
          title="Past"
          icon={<History className="text-primary" size={20} />}
          emptyText={`No reminders older than ${RECENT_REMINDER_WINDOW_DAYS} days`}
          reminders={past}
          isLoading={isLoading}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
};

export default RemindersView;
