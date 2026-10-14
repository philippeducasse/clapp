"use client";
import { Bell } from "lucide-react";
import { Reminder } from "@/interfaces/entities/Reminder";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { formatDate } from "@/utils/stringUtils";

interface ReminderBellProps {
  reminders?: Reminder[];
}

const ReminderBell = ({ reminders }: ReminderBellProps) => {
  if (!reminders?.length) return null;

  return (
    <TooltipProvider delayDuration={100}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="shrink-0 cursor-default text-amber-500" aria-label="Reminder set">
            <Bell size={14} />
          </span>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs space-y-2">
          {reminders.map((reminder) => (
            <div key={reminder.id}>
              <p className="whitespace-pre-line break-words">{reminder.message}</p>
              <p className="opacity-75">{formatDate(reminder.remindAt)}</p>
            </div>
          ))}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export { ReminderBell };
