import { PayloadAction } from "@reduxjs/toolkit";
import { ColumnFilter } from "@/interfaces/table/FilterCongig";

export interface FilterableState {
  filters: ColumnFilter[];
  globalFilter: string;
}

export const createFilterReducers = <T extends FilterableState>() => ({
  setColumnFilters(state: T, action: PayloadAction<ColumnFilter[]>) {
    state.filters = action.payload;
  },
  setColumnFilter(state: T, action: PayloadAction<ColumnFilter>) {
    const existingIndex = state.filters.findIndex((filter) => filter.id === action.payload.id);
    if (existingIndex >= 0) {
      if (action.payload.value === undefined || action.payload.value === "") {
        state.filters.splice(existingIndex, 1);
      } else {
        state.filters[existingIndex] = action.payload;
      }
    } else if (action.payload.value !== undefined && action.payload.value !== "") {
      state.filters.push(action.payload);
    }
  },
  removeColumnFilter(state: T, action: PayloadAction<string>) {
    state.filters = state.filters.filter((filter) => filter.id !== action.payload);
  },
  clearColumnFilters(state: T) {
    state.filters = [];
  },
  setGlobalFilter(state: T, action: PayloadAction<string>) {
    state.globalFilter = action.payload;
  },
});
