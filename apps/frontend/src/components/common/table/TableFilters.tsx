"use client";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Column, Table } from "@tanstack/react-table";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { getFilterInput } from "@/helpers/filterHelper";
import { Dispatch, SetStateAction } from "react";
import { FilterType } from "@/interfaces/forms/ControlledFormElementType";

interface TableFiltersProps<TData> {
  table: Table<TData>;
  filters: FilterConfig[];
  open: boolean;
  onOpenChange: Dispatch<SetStateAction<boolean>>;
}

function TableFilters<TData>({ table, filters, open, onOpenChange }: TableFiltersProps<TData>) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-1/3 border-2 ">
        <DialogHeader className="items-center w-full">
          <DialogTitle>Set filters</DialogTitle>
          <div className="flex gap-8 flex-col w-full mt-8">
            {filters.map((filter) => {
              const column = table.getColumn(filter.column) as Column<TData>;
              const value =
                filter.type === FilterType.MULTI_SELECT
                  ? (column?.getFilterValue() as string[]) ?? []
                  : filter.type === FilterType.BOOLEAN
                  ? (column?.getFilterValue() as boolean) ?? false
                  : (column?.getFilterValue() as string) ?? "";

              return (
                <div key={filter.column} className=" gap-1">
                  <div className="flex relative w-full justify-evenly items-center">
                    {getFilterInput(filter, value, column)}

                    {value && filter.type !== FilterType.MULTI_SELECT && (
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
          </div>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Close</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default TableFilters;
