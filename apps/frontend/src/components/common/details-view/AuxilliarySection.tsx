import React, { ReactNode } from "react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import DetailsView from "./DetailsView";
import EditButton from "../buttons/EditButton";
import DeleteButton from "../buttons/DeleteButton";
import { SectionCellProps } from "@/interfaces/DetailsView";

interface AuxilliarySectionProps<T> {
  title: string;
  icon: ReactNode;
  items: T[];
  entityId: number;
  formatData: (item: T) => SectionCellProps[];
  getItemKey: (item: T, idx: number) => string;
  editPath: string;
  onDelete: (index: number) => void;
}

const AuxilliarySection = <T,>({
  title,
  icon,
  items,
  entityId,
  formatData,
  getItemKey,
  editPath,
  onDelete,
}: AuxilliarySectionProps<T>) => {
  return (
    <Card className="mb-6 relative">
      <CardContent>
        <div className="flex items-center gap-2 mb-6">
          {icon}
          <CardTitle className="text-lg font-semibold text-black dark:text-foreground">
            {title}
          </CardTitle>
        </div>
        <div className="">
          {items.map((item, idx) => (
            <div key={getItemKey(item, idx)} className="flex flex-col">
              <DetailsView data={formatData(item)} />
              <div className="flex my-6 self-end mr-6 gap-2">
                <EditButton href={`${entityId}/edit/${editPath}/${idx}`} className="" />
                <DeleteButton variant="outline" onDelete={() => onDelete(idx)} />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default AuxilliarySection;
