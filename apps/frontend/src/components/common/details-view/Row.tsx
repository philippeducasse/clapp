import React, { useState } from "react";
import { SectionCellValueType, SectionCellType } from "@/interfaces/DetailsView";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { UrlObject } from "url";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";

interface RowProps {
  value: SectionCellValueType;
  type?: SectionCellType;
  title: string;
  linkTo?: UrlObject | string;
  target?: "_self" | "_blank";
  isLoading: boolean;
  disabled?: boolean;
}

const Row = ({ value, type, title, disabled, linkTo, target = "_blank", isLoading }: RowProps) => {
  const [showPassword, setShowPassword] = useState(false);

  const renderContent = () => {
    if (value instanceof Date) {
      return value.toLocaleDateString();
    }
    if (value === null || value === undefined) {
      return <span className="text-gray-400">-</span>;
    }
    switch (type) {
      case SectionCellType.Password:
        return (
          <div className="flex items-center gap-2">
            <span className={`${!showPassword ? "blur-sm select-none" : ""}`}>
              {value.toString()}
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setShowPassword(!showPassword)}
              className="h-8 w-8 p-0"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>
        );
      case SectionCellType.Link:
        return (
          <Link
            href={(linkTo as string) ?? value}
            className="text-sky-600 hover:text-sky-500 font-medium"
            target={target}
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
      case SectionCellType.HTML:
        return (
          <p
            dangerouslySetInnerHTML={{ __html: value }}
            className="prose dark:prose-invert max-w-none"
          />
        );
      default:
        return value.toString() || <span className="text-gray-400">-</span>;
    }
  };
  return (
    <div
      className={
        "grid grid-cols-2 py-3 gap-x-2 items-center border-gray-200 border-b last:border-b-0 text-sm leading-5 font-medium mx-8 my-2"
      }
    >
      {title ? (
        <>
          <dt
            className={`${
              disabled
                ? "text-gray-400"
                : "text-gray-800 dark:text-foreground text-sm leading-5 font-medium self-start"
            }`}
          >
            {title}
          </dt>
          <dd className="text-gray-700 dark:text-foreground">
            {isLoading ? <Skeleton /> : renderContent()}
          </dd>
        </>
      ) : (
        <>
          <div /> {/* Empty first column */}
          <dd className="text-gray-700 dark:text-foreground">
            {isLoading ? <Skeleton /> : renderContent()}
          </dd>
        </>
      )}
    </div>
  );
};

export default Row;
