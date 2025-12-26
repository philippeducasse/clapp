import React from "react";
import { CardTitle, CardDescription } from "@/components/ui/card";
import { TagsButton } from "../buttons/TagsButton";
import { StatusButton } from "../buttons/StatusButton";
import { TagAction } from "@/interfaces/Enums";
import { PayloadAction } from "@reduxjs/toolkit";
import { ApplicationStatus } from "@/interfaces/entities/Application";

interface DetailsViewHeaderProps<T = unknown> {
  title: string;
  icon: React.ReactNode;
  entityId?: number;
  subtitle?: string;
  actionElements?: React.ReactNode;
  tagApiMethod?: (entityId: number, action: TagAction) => Promise<T>;
  statusApiMethod?: (entityId: number, status: ApplicationStatus) => Promise<T>;
  updateSlice?: (entity: T) => PayloadAction<T>;
}

const DetailsViewHeader = <T,>({
  title,
  icon,
  subtitle,
  actionElements,
  entityId,
  tagApiMethod,
  statusApiMethod,
  updateSlice,
}: DetailsViewHeaderProps<T>) => {
  console.log({ title, subtitle });
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
