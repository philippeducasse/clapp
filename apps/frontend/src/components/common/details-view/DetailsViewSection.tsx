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
}

const DetailsViewSection = ({ title, icon, data, ribbonType, ribbonValue }: DetailsViewSectionProps) => {
  return (
    <Card className="mb-6 relative overflow-hidden">
      {ribbonType && ribbonValue && <Ribbon ribbonType={ribbonType} ribbonValue={ribbonValue} />}
      <CardContent className="grid-cols-2 ">
        <div className="flex items-center gap-2 mb-6">
          {icon}
          <CardTitle className="text-lg font-semibold text-black dark:text-foreground">
            {title}
          </CardTitle>
        </div>
        <div className="col-span-2">
          <DetailsView data={data} />
        </div>
      </CardContent>
    </Card>
  );
};

export default DetailsViewSection;
