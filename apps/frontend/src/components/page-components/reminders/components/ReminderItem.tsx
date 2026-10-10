"use client";

import Link from "next/link";
import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Reminder } from "@/interfaces/entities/Reminder";
import { OrganisationType } from "@/interfaces/Enums";
import { formatDate } from "@/utils/stringUtils";
import { cn } from "@/lib/utils";

const ORGANISATION_ROUTES: Record<OrganisationType, string> = {
  [OrganisationType.FESTIVAL]: "/festivals",
  [OrganisationType.VENUE]: "/venues",
  [OrganisationType.RESIDENCY]: "/residencies",
};

interface ReminderItemProps {
  reminder: Reminder;
  isNew?: boolean;
  onDelete?: (id: number) => void;
}

const ReminderItem = ({ reminder, isNew = false, onDelete }: ReminderItemProps) => {
  const route = ORGANISATION_ROUTES[reminder.organisationType];
  const title = reminder.organisationName || reminder.organisationType;

  return (
    <div
      className={cn(
        "p-3 rounded-lg border",
        isNew && "border-primary bg-primary/5",
      )}
    >
      <div className="flex justify-between items-start gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {reminder.organisationName && route ? (
              <Link
                href={`${route}/${reminder.objectId}`}
                className="text-primary hover:underline"
              >
                {title}
              </Link>
            ) : (
              <span className="text-primary">{title}</span>
            )}
            {isNew && <Badge>New</Badge>}
          </div>
          <p className="text-foreground break-words whitespace-pre-line">{reminder.message}</p>
          <p className="mt-1 text-sm text-muted-foreground">{formatDate(reminder.remindAt)}</p>
        </div>
        {onDelete && (
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-gray-400 hover:text-red-500"
            aria-label="Delete reminder"
            onClick={() => onDelete(reminder.id)}
          >
            <Trash2 size={16} />
          </Button>
        )}
      </div>
    </div>
  );
};

export default ReminderItem;
