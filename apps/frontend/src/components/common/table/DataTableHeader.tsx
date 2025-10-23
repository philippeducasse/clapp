import React, { useState } from "react";
import { Search } from "lucide-react";
import { Table } from "@tanstack/react-table";
import CreateButton from "../buttons/CreateButton";
import TableFilters from "./TableFilters";
import { Button } from "@/components/ui/button";
import { SlidersHorizontal } from "lucide-react";
import { FilterConfig } from "@/interfaces/table/FilterCongig";

interface DataTableHeaderProps<TData> {
  globalFilter: string;
  setGlobalFilter: (value: string) => void;
  entityName: string;
  table: Table<TData>;
  filters?: FilterConfig[];
}

const DataTableHeader = <TData,>({
  globalFilter,
  setGlobalFilter,
  entityName,
  table,
  filters,
}: DataTableHeaderProps<TData>) => {
  const [openFilterDialog, setOpenFilterDialog] = useState(false);
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex max-w-sm h-10 items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2 dark:bg-background dark:border-gray-700">
          <Search className="h-[16px] w-[16px]" />
          <input
            placeholder="Search"
            value={globalFilter}
            onChange={(event) => setGlobalFilter(event.target.value)}
            type="search"
            className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:text-foreground"
          />
        </div>
        <div className="flex gap-4">
          <Button variant={"tertiary"} onClick={() => setOpenFilterDialog(true)}>
            <SlidersHorizontal />
            Filters
          </Button>
          <CreateButton
            label={`Create new ${entityName}`}
            href={entityName !== "residency" ? `${entityName}s/create` : "residencies/create"}
          />
        </div>
      </div>
      {filters && (
        <TableFilters
          table={table}
          filters={filters}
          open={openFilterDialog}
          onOpenChange={setOpenFilterDialog}
        />
      )}
    </div>
  );
};

export default DataTableHeader;
