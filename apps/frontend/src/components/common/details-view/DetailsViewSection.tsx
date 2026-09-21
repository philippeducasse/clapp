import React from "react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import DetailsView from "./DetailsView";
import { SectionCellProps } from "@/interfaces/DetailsView";
import Ribbon from "../Ribbon";

interface DetailsViewSectionProps {
  title: string;
  icon: React.ReactNode;
  data: SectionCellProps[];
  ribbonType?: "tag" | "status";
  ribbonValue?: string;
  sideText?: string;
  subtitle?: React.ReactNode;
  emptyMessage?: string;
  action?: React.ReactNode;
}

const DetailsViewSection = ({
  title,
  icon,
  data,
  ribbonType,
  ribbonValue,
  sideText,
  subtitle,
  action,
}: DetailsViewSectionProps) => {
  return (
    <div className={`${sideText ? "flex" : ""}`}>
      {sideText && <p className="flex-1 p-2">{sideText}</p>}
      <Card className="mb-6 relative overflow-hidden flex-2">
        {ribbonType && ribbonValue && <Ribbon ribbonType={ribbonType} ribbonValue={ribbonValue} />}
        <CardContent>
          <div className="flex items-center justify-between gap-2 mb-6">
            <div className="flex items-center gap-2">
              {icon}
              <CardTitle className="text-lg font-semibold text-black dark:text-foreground">
                {title}
              </CardTitle>
              {subtitle && (
                <CardTitle className="font-light text-gray-600 dark:text-foreground">
                  {subtitle}
                </CardTitle>
              )}
            </div>
            {action && <div>{action}</div>}
          </div>
          <div className="col-span-2">
            {data.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 italic ml-2">{`No ${title.toLowerCase()}`}</p>
            ) : (
              <DetailsView data={data} />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DetailsViewSection;
