import React from "react";
import { SectionCellValueType, SectionCellType } from "@/interfaces/DetailsView";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface RowProps {
  value: SectionCellValueType;
  type?: SectionCellType;
  title: string;
  linkTo?: string;
  target?: string;
  isLoading: boolean;
  disabled?: boolean;
}

const Row = ({ value, type, title, disabled, linkTo, target, isLoading }: RowProps) => {
  const renderContent = () => {
    if (value instanceof Date) {
      return value.toLocaleDateString();
    }
    if (value === null || value === undefined) {
      return <span className="text-gray-400">-</span>;
    }
    switch (type) {
      case SectionCellType.Link:
        return (
          <Link
            href={(linkTo as string) ?? value}
            className="text-sky-600 hover:text-sky-500 font-medium"
            target={target ?? "_blank"}
          >
            {value as React.ReactNode}
          </Link>
        );
      case SectionCellType.Badge:
        return (
          <Badge
            color="red"
            // color={getBadgeColorByStatus(value as Status)}
            variant="secondary"
          />
        );
      case SectionCellType.Bool:
        return value ? "Yes" : "No";
      default:
        return value.toString() || <span className="text-gray-400">-</span>;
    }
  };

  return (
    <div
      className={
        "grid grid-cols-2 py-3 gap-x-2 items-center border-gray-200 border-b last:border-b-0 text-sm leading-5 font-medium ml-8 my-2"
      }
    >
      {title && (
        <dt className={`${disabled ? "text-gray-400" : "text-gray-800 text-sm leading-5 font-medium"}`}>{title}</dt>
      )}
      <dd className="text-gray-700">{isLoading ? <Skeleton /> : renderContent()}</dd>
    </div>
  );
};

export default Row;
