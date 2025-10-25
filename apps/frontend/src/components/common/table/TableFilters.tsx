"use client";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Table } from "@tanstack/react-table";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { getFilterInput } from "@/helpers/FilterHelper";

interface TableFiltersProps<TData> {
  table: Table<TData>;
  filters: FilterConfig[];
  open: boolean;
  onOpenChange: () => void;
}

function TableFilters<TData>({ table, filters, open, onOpenChange }: TableFiltersProps<TData>) {
  const hasActiveFilters = filters.some((filter) => {
    const column = table.getColumn(filter.column);
    return column?.getFilterValue();
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-1/3 border-2 ">
        <DialogHeader className="items-center">
          <DialogTitle>Set filters</DialogTitle>
          <div className="flex items-center gap-2 flex-wrap">
            {filters.map((filter) => {
              const column = table.getColumn(filter.column);
              const value = (column?.getFilterValue() as string) ?? "";

              return (
                <div key={filter.column} className="flex items-center gap-1">
                  <div className="relative">
                    {getFilterInput(filter, value, column)}

                    {value && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 p-0 hover:bg-transparent"
                        onClick={() => column?.setFilterValue(undefined)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2 text-xs"
                onClick={() => table.resetColumnFilters()}
              >
                Clear all
              </Button>
            )}
          </div>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button>Set</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default TableFilters;
