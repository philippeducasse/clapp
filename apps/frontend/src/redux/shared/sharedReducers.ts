import { PayloadAction, AsyncThunk, ActionReducerMapBuilder } from "@reduxjs/toolkit";
import { ColumnFilter } from "@/interfaces/table/FilterCongig";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";

export interface BaseSliceState {
  loading: boolean;
  error: string | null;
  filters: ColumnFilter[];
  searchBarFilter: string;
}

export const createFilterReducers = <T extends BaseSliceState>() => ({
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
  setSearchBarFilter(state: T, action: PayloadAction<string>) {
    state.searchBarFilter = action.payload;
  },
});

export const createAsyncExtraReducers =
  <Entity, T extends BaseSliceState>(
    asyncThunk: AsyncThunk<PaginatedResponse<Entity>, void, object>,
    dataKey: string,
  ) =>
  (builder: ActionReducerMapBuilder<T>) => {
    builder
      .addCase(asyncThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(asyncThunk.fulfilled, (state, action: PayloadAction<PaginatedResponse<Entity>>) => {
        state.loading = false;
        (state as Record<string, Entity[]>)[dataKey] = action.payload.results;
      })
      .addCase(asyncThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch";
      });
  };
