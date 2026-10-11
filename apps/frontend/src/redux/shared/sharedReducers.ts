import { PayloadAction, AsyncThunk, ActionReducerMapBuilder } from "@reduxjs/toolkit";
import { ColumnFilter } from "@/interfaces/table/FilterCongig";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";

export interface BaseSliceState {
  loading: boolean;
  error: string | null;
  filters: ColumnFilter[];
  searchBarFilter: string;
  // True once filters have been set (by the user, a default, or server-provided
  // initial filters). Defaults must only be applied while this is false.
  filtersInitialized: boolean;
}

export const createFilterReducers = <T extends BaseSliceState>() => ({
  setColumnFilters(state: T, action: PayloadAction<ColumnFilter[]>) {
    state.filters = action.payload;
    state.filtersInitialized = true;
  },
  setColumnFilter(state: T, action: PayloadAction<ColumnFilter>) {
    state.filtersInitialized = true;
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
    state.filtersInitialized = true;
  },
  clearColumnFilters(state: T) {
    state.filters = [];
    state.filtersInitialized = true;
  },
  // Sets filters only if they haven't been initialized yet (no-op otherwise).
  initializeColumnFilters(state: T, action: PayloadAction<ColumnFilter[]>) {
    if (state.filtersInitialized) return;
    state.filters = action.payload;
    state.filtersInitialized = true;
  },
  setSearchBarFilter(state: T, action: PayloadAction<string>) {
    state.searchBarFilter = action.payload;
  },
});

export const createAsyncExtraReducers =
  <Entity, T extends BaseSliceState, TArg = void>(
    asyncThunk: AsyncThunk<PaginatedResponse<Entity>, TArg, object>,
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
