"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  ColumnFiltersState,
  getFilteredRowModel,
  SortingState,
  getSortedRowModel,
  PaginationState,
  OnChangeFn,
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
import { useDispatch, useSelector } from "react-redux";
import DataTableHeader from "./DataTableHeader";
import { TableEntityName } from "@/interfaces/Enums";
import { tableFilterSlices } from "@/redux/shared/tableFilterSlices";
import { toFilterParams } from "@/helpers/defaultFilters";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";

interface FetchParams {
  offset: number;
  limit: number;
  search?: string;
  filters?: Record<string, unknown>;
}

const DEFAULT_PAGE_SIZE = 25;

const buildFetchParams = (
  pagination: PaginationState,
  columnFilters: ColumnFiltersState,
  searchBarFilter: string,
): FetchParams => {
  const filterParams = toFilterParams(columnFilters);
  return {
    offset: pagination.pageIndex * pagination.pageSize,
    limit: pagination.pageSize,
    search: searchBarFilter || undefined,
    filters: Object.keys(filterParams).length > 0 ? filterParams : undefined,
  };
};

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  /** Server-rendered first page, fetched with `initialColumnFilters`, no search, offset 0. */
  data: TData[];
  entityName: TableEntityName;
  totalCount?: number;
  filters?: FilterConfig[];
  defaultSorting?: SortingState;
  /**
   * Filters the server used to fetch `data`. Used until the entity slice's filters
   * are initialized, then written to the slice once (no-op if already initialized).
   */
  initialColumnFilters?: ColumnFiltersState;
  fetchData?: (params: FetchParams) => Promise<PaginatedResponse<TData>>;
  onDataFetched?: (data: PaginatedResponse<TData>) => void;
}

const EMPTY_FILTERS: ColumnFiltersState = [];

export function DataTable<TData, TValue>({
  columns,
  data,
  entityName,
  totalCount,
  filters,
  defaultSorting = [],
  initialColumnFilters = EMPTY_FILTERS,
  fetchData,
  onDataFetched,
}: DataTableProps<TData, TValue>) {
  const dispatch = useDispatch();
  const filterSlice = tableFilterSlices[entityName];
  const [sorting, setSorting] = useState<SortingState>(defaultSorting);

  // Column filters and search live in the entity's Redux slice, so they persist
  // across navigation and can be defaulted from the slice (e.g. default season).
  // Until the slice is initialized, use the filters the server rendered with,
  // so the first render matches the server data (no flash of unfiltered rows).
  const filterState = useSelector(filterSlice.selectFilterState);
  const columnFilters: ColumnFiltersState = filterState.filtersInitialized
    ? filterState.filters
    : initialColumnFilters;
  const searchBarFilter = filterState.searchBarFilter;

  useEffect(() => {
    if (initialColumnFilters.length > 0) {
      dispatch(filterSlice.initializeColumnFilters(initialColumnFilters));
    }
  }, [dispatch, filterSlice, initialColumnFilters]);

  const setColumnFilters: OnChangeFn<ColumnFiltersState> = useCallback(
    (updater) => {
      const next = typeof updater === "function" ? updater(columnFilters) : updater;
      dispatch(filterSlice.setColumnFilters(next));
    },
    [columnFilters, dispatch, filterSlice],
  );
  const setSearchBarFilter = useCallback(
    (value: string) => dispatch(filterSlice.setSearchBarFilter(value)),
    [dispatch, filterSlice],
  );
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: DEFAULT_PAGE_SIZE,
  });

  const handlePaginationChange: OnChangeFn<PaginationState> = useCallback((updater) => {
    setPagination((prev) => {
      const newPagination = typeof updater === "function" ? updater(prev) : updater;
      return newPagination;
    });
  }, []);

  // Push the server-rendered data to the parent once on mount
  const hasSentInitialData = useRef(false);
  useEffect(() => {
    if (hasSentInitialData.current) return;
    hasSentInitialData.current = true;
    if (data.length > 0 && onDataFetched) {
      onDataFetched({
        results: data,
        count: totalCount || data.length,
      } as PaginatedResponse<TData>);
    }
  }, [data, totalCount, onDataFetched]);

  // Key of the params the currently shown data was fetched with. Starts as the
  // server's request, so we don't refetch on mount unless the params differ
  // (e.g. persisted filters/search from a previous visit).
  const lastRequestKey = useRef(
    JSON.stringify(
      buildFetchParams({ pageIndex: 0, pageSize: DEFAULT_PAGE_SIZE }, initialColumnFilters, ""),
    ),
  );

  // Fetch data when pagination, filters, or search changes
  useEffect(() => {
    if (!fetchData) return;
    const params = buildFetchParams(pagination, columnFilters, searchBarFilter);
    const key = JSON.stringify(params);
    if (key === lastRequestKey.current) return;
    lastRequestKey.current = key;

    fetchData(params).then((response) => {
      // Ignore stale responses if params changed while the request was in flight
      if (lastRequestKey.current === key) onDataFetched?.(response);
    });
  }, [pagination, columnFilters, searchBarFilter, fetchData, onDataFetched]);

  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setSearchBarFilter,
    getFilteredRowModel: getFilteredRowModel(),
    onPaginationChange: handlePaginationChange,
    manualPagination: true,
    pageCount: totalCount ? Math.ceil(totalCount / pagination.pageSize) : undefined,
    state: {
      sorting,
      columnFilters,
      globalFilter: searchBarFilter,
      pagination,
    },
  });
  // Reset to page 0 when filters or search changes
  useEffect(() => {
    setPagination((prev) => ({ pageIndex: 0, pageSize: prev.pageSize }));
  }, [columnFilters, searchBarFilter]);

  return (
    <>
      <Card className="rounded-md border px-6">
        <DataTableHeader
          searchBarFilter={searchBarFilter}
          setSearchBarFilter={setSearchBarFilter}
          entityName={entityName.toLowerCase()}
          table={table}
          filters={filters}
        />
        <Table style={{ tableLayout: "fixed" }}>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} style={{ width: `${header.getSize()}px` }}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
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
      <TablePagination
        table={table}
        pagination={pagination}
        entityName={entityName}
        totalCount={totalCount}
      />
    </>
  );
}
