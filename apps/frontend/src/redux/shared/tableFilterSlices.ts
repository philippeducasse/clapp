import { PayloadAction } from "@reduxjs/toolkit";
import { EntityName, TableEntityName } from "@/interfaces/Enums";
import { ColumnFilter } from "@/interfaces/table/FilterCongig";
import { RootState } from "../store";
import { BaseSliceState } from "./sharedReducers";
import * as festivalSlice from "../slices/festivalSlice";
import * as venueSlice from "../slices/venueSlice";
import * as residencySlice from "../slices/residencySlice";
import * as applicationSlice from "../slices/applicationSlice";

export interface TableFilterSlice {
  selectFilterState: (state: RootState) => BaseSliceState;
  setColumnFilters: (filters: ColumnFilter[]) => PayloadAction<ColumnFilter[]>;
  initializeColumnFilters: (filters: ColumnFilter[]) => PayloadAction<ColumnFilter[]>;
  setSearchBarFilter: (value: string) => PayloadAction<string>;
}

// Each table keeps its filters/search in its own entity slice.
export const tableFilterSlices: Record<TableEntityName, TableFilterSlice> = {
  [EntityName.FESTIVAL]: {
    selectFilterState: (state) => state.festivals,
    setColumnFilters: festivalSlice.setColumnFilters,
    initializeColumnFilters: festivalSlice.initializeColumnFilters,
    setSearchBarFilter: festivalSlice.setSearchBarFilter,
  },
  [EntityName.VENUE]: {
    selectFilterState: (state) => state.venues,
    setColumnFilters: venueSlice.setColumnFilters,
    initializeColumnFilters: venueSlice.initializeColumnFilters,
    setSearchBarFilter: venueSlice.setSearchBarFilter,
  },
  [EntityName.RESIDENCY]: {
    selectFilterState: (state) => state.residencies,
    setColumnFilters: residencySlice.setColumnFilters,
    initializeColumnFilters: residencySlice.initializeColumnFilters,
    setSearchBarFilter: residencySlice.setSearchBarFilter,
  },
  [EntityName.APPLICATION]: {
    selectFilterState: (state) => state.applications,
    setColumnFilters: applicationSlice.setColumnFilters,
    initializeColumnFilters: applicationSlice.initializeColumnFilters,
    setSearchBarFilter: applicationSlice.setSearchBarFilter,
  },
};
