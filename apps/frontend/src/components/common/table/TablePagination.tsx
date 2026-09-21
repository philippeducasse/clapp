"use client";

import React from "react";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Table } from "@tanstack/react-table";
import { EntityName } from "@/interfaces/Enums";
import { capitalizeFirst } from "@/utils/stringUtils";

interface TablePaginationProps<TData> {
  table: Table<TData>;
  entityName: EntityName;
  pagination: {
    pageIndex: number;
    pageSize: number;
  };
  totalCount?: number;
}

function TablePagination<TData>({
  table,
  pagination,
  entityName,
  totalCount,
}: TablePaginationProps<TData>) {
  const currentPage = pagination.pageIndex + 1;

  const totalPages = totalCount
    ? Math.ceil(totalCount / pagination.pageSize)
    : Math.ceil(table.getFilteredRowModel().rows.length / pagination.pageSize);

  const totalItems = totalCount ? totalCount : table.getFilteredRowModel().rows.length;

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

  const handlePageSizeChange = (newPageSize: string) => {
    if (newPageSize === "All") {
      table.setPageSize(totalItems);
    } else {
      const size = parseInt(newPageSize);
      table.setPageSize(size);
    }
    table.setPageIndex(0);
  };

  const pageSizeOptions = [10, 25, 50, 100, "All"];
  return (
    <Pagination className="justify-between mt-8">
      <div className="flex items-center gap-4">
        <div>
          Page {currentPage} of {totalPages} | Total {capitalizeFirst(entityName)}s: {totalItems}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm">Per page:</span>
          <Select value={String(pagination.pageSize)} onValueChange={handlePageSizeChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {pageSizeOptions.map((size) => (
                <SelectItem key={size} value={String(size)}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
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
            <PaginationLink
              onClick={() => table.setPageIndex(pageNumber - 1)}
              isActive={currentPage === pageNumber}
            >
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
  );
}

export default TablePagination;
