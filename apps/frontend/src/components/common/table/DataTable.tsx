"use client";
import { useState } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  getFilteredRowModel,
  SortingState,
  getSortedRowModel,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card } from "@/components/ui/card";
import TablePagination from "./TablePagination";
import { EntityName } from "@/interfaces/Enums";
import DataTableHeader from "./DataTableHeader";
interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  entityName: EntityName;
  pagination?: {
    pageIndex: number;
    pageSize: number;
  };
  setPagination?: (pagination: { pageIndex: number; pageSize: number }) => void;
  totalCount?: number;
  isLoading?: boolean;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  entityName,
  pagination: externalPagination,
  setPagination: setExternalPagination,
  totalCount,
  isLoading = false,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState<string>("");
  const [internalPagination, setInternalPagination] = useState({
    pageIndex: 0,
    pageSize: 30,
  });

  // Use external pagination if provided, otherwise use internal
  const pagination = externalPagination || internalPagination;
  const setPagination = setExternalPagination || setInternalPagination;
  const isServerSide = !!externalPagination;

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    onGlobalFilterChange: setGlobalFilter,
    getFilteredRowModel: getFilteredRowModel(),
    onPaginationChange: setPagination,
    manualPagination: isServerSide,
    pageCount: isServerSide && totalCount ? Math.ceil(totalCount / pagination.pageSize) : undefined,
    state: {
      sorting,
      globalFilter,
      pagination,
    },
  });

  return (
    <div>
      <Card className="rounded-md border px-6">
        <DataTableHeader
          globalFilter={globalFilter}
          setGlobalFilter={setGlobalFilter}
          entityName={entityName}
        />
        <Table className="">
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead
                      key={header.id}
                      style={{ width: `${header.getSize()}px` }}
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell
                      key={cell.id}
                      style={{ width: `${cell.column.getSize()}px` }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
      <TablePagination
        table={table}
        pagination={pagination}
        entityName={entityName}
        totalCount={totalCount}
        isServerSide={isServerSide}
      />
    </div>
  );
}
