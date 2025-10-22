import React from "react";
import { CardTitle, CardDescription } from "@/components/ui/card";
import { TagsButton } from "../buttons/TagsButton";
import { festivalApiService } from "@/api/festivalApiService";

interface DetailsViewHeaderProps {
  title: string;
  icon: React.ReactNode;
  entityId?: number;
  subtitle?: string;
  actionElements?: React.ReactNode;
}

const DetailsViewHeader = ({
  title,
  icon,
  subtitle,
  actionElements,
  entityId,
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
          {entityId && <TagsButton mark={festivalApiService.mark} entityId={entityId} />}
        </div>
      )}
    </div>
  );
};

export default DetailsViewHeader;
