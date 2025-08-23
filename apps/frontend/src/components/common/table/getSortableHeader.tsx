"use client";
import { HeaderContext } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";

export const getSortableHeader = <T,>(columnName: string) => {
  const SortableHeader = ({ column }: HeaderContext<T, unknown>) => {
    return (
      <Button className="-ml-3" variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
        {columnName}
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    );
  };

  // Add displayName for debugging
  SortableHeader.displayName = `SortableHeader(${columnName})`;

  return SortableHeader;
};
