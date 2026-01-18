import React, { useState } from "react";
import { CardTitle, CardDescription } from "@/components/ui/card";
import { TagsButton } from "../buttons/TagsButton";
import { StatusButton } from "../buttons/StatusButton";
import { OrganisationType, TagAction } from "@/interfaces/Enums";
import { PayloadAction } from "@reduxjs/toolkit";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { Button } from "@/components/ui/button";
import { AlarmClock } from "lucide-react";
import { ReminderModal } from "../modals/ReminderModal";
import { Reminder, ReminderCreate } from "@/interfaces/entities/Reminder";

interface DetailsViewHeaderProps<T = unknown> {
  title: string;
  icon: React.ReactNode;
  entityId?: number;
  organisationType?: OrganisationType;
  subtitle?: string;
  actionElements?: React.ReactNode;
  tagApiMethod?: (entityId: number, action: TagAction) => Promise<T>;
  reminderApiMethod?: (reminder: ReminderCreate) => Promise<Reminder>;
  statusApiMethod?: (entityId: number, status: ApplicationStatus) => Promise<T>;
  updateSlice?: (entity: T) => PayloadAction<T>;
}

const DetailsViewHeader = <T,>({
  title,
  icon,
  subtitle,
  actionElements,
  entityId,
  organisationType,
  tagApiMethod,
  statusApiMethod,
  reminderApiMethod,
  updateSlice,
}: DetailsViewHeaderProps<T>) => {
  const [openReminderModal, setOpenReminderModal] = useState(false);

  return (
    <div className="flex justify-between my-6">
      <div className="flex items-center gap-2">
        {icon}
        <div className="flex flex-col md:flex-row gap-2 items-start md:items-center">
          <CardTitle className="max-w-prose h-fit">{title}</CardTitle>
          {subtitle && <CardDescription>{subtitle}</CardDescription>}
        </div>
      </div>
      {actionElements && (
        <div className="flex gap-6 self-end mx-8 items-stretch">
          {actionElements}
          {entityId && tagApiMethod && updateSlice && (
            <TagsButton tag={tagApiMethod} entityId={entityId} updateSlice={updateSlice} />
          )}
          {entityId && reminderApiMethod && organisationType && (
            <>
              <Button variant="tertiary" onClick={() => setOpenReminderModal(true)}>
                <AlarmClock />
              </Button>
              {openReminderModal && (
                <ReminderModal
                  open={openReminderModal}
                  onOpenChange={setOpenReminderModal}
                  reminderApiMethod={reminderApiMethod}
                  organisationType={organisationType}
                  entityId={entityId}
                />
              )}
            </>
          )}
          {entityId && statusApiMethod && updateSlice && (
            <StatusButton
              updateStatus={statusApiMethod}
              entityId={entityId}
              updateSlice={updateSlice}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default DetailsViewHeader;
