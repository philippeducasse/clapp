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
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Search } from "lucide-react";
import { Card } from "@/components/ui/card";
import CreateButton from "../buttons/CreateButton";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  entityName: string;
}

export function DataTable<TData, TValue>({ columns, data, entityName }: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState<string>("");
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 30,
  });

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
    state: {
      sorting,
      globalFilter,
      pagination,
    },
  });

  // Calculate the current page number (1-based)
  const currentPage = pagination.pageIndex + 1;

  // Calculate the total number of pages
  const totalPages = Math.ceil(table.getFilteredRowModel().rows.length / pagination.pageSize);

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pageNumbers = [];
    const maxVisiblePages = 5; // Max number of page links to show
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    // Adjust if we're at the end of the range
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(i);
    }

    return pageNumbers;
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="flex mb-6 max-w-sm h-10 items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2 dark:bg-background dark:border-gray-700">
          <Search className="h-[16px] w-[16px]" />
          <input
            placeholder="Search"
            value={globalFilter}
            onChange={(event) => setGlobalFilter(event.target.value)}
            type="search"
            className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:text-foreground"
          />
        </div>
        <CreateButton label={`Create new ${entityName}`} href={`${entityName}s/create`} />
      </div>
      <Card className="rounded-md border px-6">
        <Table className="">
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} style={{ width: `${header.getSize()}px` }}>
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} style={{ width: `${cell.column.getSize()}px` }}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
      <Pagination className="justify-between mt-8">
        <div className="">
          Page {currentPage} of {totalPages} | Total Festivals: {table.getFilteredRowModel().rows.length}
        </div>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious onClick={() => table.previousPage()} />
          </PaginationItem>

          {/* Show first page with ellipsis if needed */}
          {currentPage > 3 && (
            <>
              <PaginationItem>
                <PaginationLink onClick={() => table.setPageIndex(0)} isActive={currentPage === 1}>
                  1
                </PaginationLink>
              </PaginationItem>
              {currentPage > 4 && (
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
              )}
            </>
          )}

          {/* Show page numbers */}
          {getPageNumbers().map((pageNumber) => (
            <PaginationItem key={pageNumber}>
              <PaginationLink onClick={() => table.setPageIndex(pageNumber - 1)} isActive={currentPage === pageNumber}>
                {pageNumber}
              </PaginationLink>
            </PaginationItem>
          ))}

          {/* Show last page with ellipsis if needed */}
          {currentPage < totalPages - 2 && (
            <>
              {currentPage < totalPages - 3 && (
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
              )}
              <PaginationItem>
                <PaginationLink
                  onClick={() => table.setPageIndex(totalPages - 1)}
                  isActive={currentPage === totalPages}
                >
                  {totalPages}
                </PaginationLink>
              </PaginationItem>
            </>
          )}

          <PaginationItem>
            <PaginationNext onClick={() => table.nextPage()} />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
}
