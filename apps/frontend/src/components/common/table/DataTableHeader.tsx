import React, { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { Table } from "@tanstack/react-table";
import CreateButton from "../buttons/CreateButton";
import TableFilters from "./TableFilters";
import { Button } from "@/components/ui/button";
import { SlidersHorizontal } from "lucide-react";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { X } from "lucide-react";
import _ from "lodash";
import { useDispatch } from "react-redux";
import { useSelector } from "react-redux";
import {
  selectColumnFilters,
  selectGlobalFilter,
  setColumnFilters,
  setGlobalFilter as setReduxGlobalFilter,
  removeColumnFilter,
} from "@/redux/slices/festivalSlice";

interface DataTableHeaderProps<TData> {
  globalFilter: string;
  entityName: string;
  table: Table<TData>;
  filters?: FilterConfig[];
}

const DataTableHeader = <TData,>({
  globalFilter,
  entityName,
  table,
  filters,
}: DataTableHeaderProps<TData>) => {
  const dispatch = useDispatch();

  const reduxFilters = useSelector(selectColumnFilters);
  const reduxGlobalFilter = useSelector(selectGlobalFilter);
  const [openFilterDialog, setOpenFilterDialog] = useState(false);

  useEffect(() => {
    if (reduxFilters.length > 0) {
      table.setColumnFilters(reduxFilters);
    }
    if (reduxGlobalFilter) {
      table.setGlobalFilter(reduxGlobalFilter);
    }
  }, [table, reduxFilters, reduxGlobalFilter]);

  useEffect(() => {
    const columnFilters = table.getState().columnFilters;
    dispatch(setColumnFilters(columnFilters));
  }, [table, dispatch]);

  useEffect(() => {
    const globalFilter = table.getState().globalFilter ?? "";
    dispatch(setReduxGlobalFilter(globalFilter));
  }, [table, dispatch]);

  const activeFilters =
    filters
      ?.map((filter) => {
        const column = table.getColumn(filter.column);
        const value = column?.getFilterValue();
        if (value) {
          if (Array.isArray(value)) {
            return value.map((v) => ({
              column: filter.column,
              value: v,
            }));
          }
          return {
            column: filter.column,
            value,
          };
        }
        return null;
      })
      .filter(Boolean) ?? [];

  const handleRemoveFilter = (columnId: string, valueToRemove?: unknown) => {
    const column = table.getColumn(columnId);
    const currentValue = column?.getFilterValue();

    if (Array.isArray(currentValue)) {
      const newValue = currentValue.filter((v) => v !== valueToRemove);

      if (newValue.length === 0) {
        column?.setFilterValue(undefined);
        dispatch(removeColumnFilter(columnId));
      } else {
        column?.setFilterValue(newValue);
        dispatch(setColumnFilters([{ id: columnId, value: newValue }]));
      }
    } else {
      column?.setFilterValue(undefined);
      dispatch(removeColumnFilter(columnId));
    }
  };

  const handleGlobalFilterChange = (value: string) => {
    table.setGlobalFilter(value);
    dispatch(setReduxGlobalFilter(value));
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex gap-6">
          <div className="flex max-w-sm h-10 items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2 dark:bg-background dark:border-gray-700">
            <Search className="h-[16px] w-[16px]" />
            <input
              placeholder="Search"
              value={globalFilter}
              onChange={(event) => handleGlobalFilterChange(event.target.value)}
              type="search"
              className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:text-foreground"
            />
          </div>
          <div className="flex ">
            {activeFilters && activeFilters.length > 0 && (
              <div className="flex flex-wrap gap-2 items-center">
                {activeFilters.flat().map((filter) => {
                  return (
                    <Button
                      key={filter?.value}
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-xs gap-1"
                      onClick={() => handleRemoveFilter(filter?.column as string, filter?.value)}
                    >
                      <span>{_.capitalize(String(filter?.value))}</span>
                      <X className="h-3 w-3 ml-1" />
                    </Button>
                  );
                })}
              </div>
            )}
          </div>
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
