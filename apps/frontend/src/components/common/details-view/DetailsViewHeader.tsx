import React from "react";
import { CardTitle, CardDescription } from "@/components/ui/card";

interface DetailsViewHeaderProps {
  title: string;
  icon: React.ReactNode;
  subtitle?: string;
  actionElements?: React.ReactNode;
}

const DetailsViewHeader = ({ title, icon, subtitle, actionElements }: DetailsViewHeaderProps) => {
  return (
    <div className="flex justify-between my-6">
      <div className="flex items-center gap-2">
        {icon}
        <div className="flex flex-col md:flex-row gap-2 items-start md:items-center">
          <CardTitle className="max-w-prose h-fit">{title}</CardTitle>
          {subtitle && <CardDescription>{subtitle}</CardDescription>}
        </div>
      </div>
      {actionElements && <div className="flex gap-6 self-end mx-8 items-stretch">{actionElements}</div>}
    </div>
  );
};

export default DetailsViewHeader;
