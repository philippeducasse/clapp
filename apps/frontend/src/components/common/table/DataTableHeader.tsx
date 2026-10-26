import React, { useState } from "react";
import { Search } from "lucide-react";
import { Table } from "@tanstack/react-table";
import CreateButton from "../buttons/CreateButton";
import TableFilters from "./TableFilters";
import { Button } from "@/components/ui/button";
import { SlidersHorizontal } from "lucide-react";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { X } from "lucide-react";
import { capitalizeFirst } from "@/utils/stringUtils";

interface DataTableHeaderProps<TData> {
  searchBarFilter: string;
  setSearchBarFilter: (value: string) => void;
  entityName: string;
  table: Table<TData>;
  filters?: FilterConfig[];
}

const DataTableHeader = <TData,>({
  searchBarFilter,
  setSearchBarFilter,
  entityName,
  table,
  filters,
}: DataTableHeaderProps<TData>) => {
  const [openFilterDialog, setOpenFilterDialog] = useState(false);

  const activeFilters =
    filters?.flatMap((filter) => {
      const value = table.getColumn(filter.column)?.getFilterValue();
      if (!value) return [];
      const values = Array.isArray(value) ? value : [value];
      return values.map((v) => {
        const label =
          filter.options?.find((option) => option.value === v)?.label ?? capitalizeFirst(String(v));
        return {
          column: filter.column,
          value: v,
          label: filter.chipPrefix ? `${filter.chipPrefix} ${label.toLowerCase()}` : label,
        };
      });
    }) ?? [];

  const handleRemoveFilter = (columnId: string, valueToRemove?: unknown) => {
    const column = table.getColumn(columnId);
    const currentValue = column?.getFilterValue();

    if (Array.isArray(currentValue)) {
      const newValue = currentValue.filter((v) => v !== valueToRemove);
      column?.setFilterValue(newValue.length === 0 ? undefined : newValue);
    } else {
      column?.setFilterValue(undefined);
    }
  };

  const handlesearchBarFilterChange = (value: string) => {
    setSearchBarFilter(value);
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex gap-6">
          <div className="flex max-w-sm h-10 items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2 dark:bg-background dark:border-gray-700">
            <Search className="h-[16px] w-[16px] text-primary" />
            <input
              placeholder="Search"
              value={searchBarFilter}
              onChange={(event) =>
                handlesearchBarFilterChange(event.target.value)
              }
              type="search"
              className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:text-foreground"
            />
          </div>
          <div className="flex ">
            {activeFilters.length > 0 && (
              <div className="flex flex-wrap gap-2 items-center">
                {activeFilters.map((filter) => {
                  return (
                    <Button
                      key={`${filter.column}-${String(filter.value)}`}
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-xs gap-1"
                      onClick={() => handleRemoveFilter(filter.column, filter.value)}
                    >
                      <span>{filter.label}</span>
                      <X className="h-3 w-3 ml-1 text-primary" />
                    </Button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-4">
          {filters && (
            <Button
              variant={"secondary"}
              onClick={() => setOpenFilterDialog(true)}
            >
              <SlidersHorizontal className="text-primary" />
              Filters
            </Button>
          )}
          <CreateButton
            label={`Create new ${capitalizeFirst(entityName)}`}
            href={
              entityName !== "residency"
                ? `${entityName}s/create`
                : "residencies/create"
            }
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
