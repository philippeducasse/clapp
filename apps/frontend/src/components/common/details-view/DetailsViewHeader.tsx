import React from "react";
import { CardTitle, CardDescription } from "@/components/ui/card";
import { TagsButton } from "../buttons/TagsButton";
import { festivalApiService } from "@/api/festivalApiService";
import { updateFestival } from "@/redux/slices/festivalSlice";

interface DetailsViewHeaderProps {
  title: string;
  icon: React.ReactNode;
  entityId?: number;
  subtitle?: string;
  actionElements?: React.ReactNode;
  showTags?: boolean;
}

const DetailsViewHeader = ({
  title,
  icon,
  subtitle,
  actionElements,
  entityId,
  showTags = true,
}: DetailsViewHeaderProps) => {
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
          {entityId && showTags && (
            <TagsButton
              tag={festivalApiService.tag}
              entityId={entityId}
              updateSlice={updateFestival}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default DetailsViewHeader;
