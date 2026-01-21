import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Residency } from "@/interfaces/entities/Residency";
import { RootState } from "../store";
import { residencyApiService } from "@/api/residencyApiService";
import { GetAllParams } from "@/interfaces/api/ApiService";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { createFilterReducers, BaseSliceState, createAsyncExtraReducers } from "../shared/sharedReducers";

interface ResidenciesState extends BaseSliceState {
  residencies: Residency[];
}

const initialState: ResidenciesState = {
  residencies: [],
  filters: [],
  searchBarFilter: "",
  loading: false,
  error: null,
};

export const fetchResidencies = createAsyncThunk<PaginatedResponse<Residency>, GetAllParams | undefined>(
  "residencies/fetchResidencies",
  async (params?: GetAllParams) => {
    const response = await residencyApiService.getAll(params);
    return response;
  },
);

const residencySlice = createSlice({
  name: "residencies",
  initialState,
  reducers: {
    setResidencies(state, action: PayloadAction<Residency[]>) {
      state.residencies = action.payload;
    },
    setResidency(state, action: PayloadAction<Residency>) {
      const existingIndex = state.residencies.findIndex(
        (residency) => residency.id === action.payload.id
      );
      if (existingIndex >= 0) {
        state.residencies[existingIndex] = action.payload;
      } else {
        state.residencies.push(action.payload);
      }
    },
    addResidency(state, action: PayloadAction<Residency>) {
      state.residencies.push(action.payload);
    },
    updateResidency(state, action: PayloadAction<Residency>) {
      const { id } = action.payload;
      const existingResidency = state.residencies.find((residency) => residency.id === id);
      if (existingResidency) {
        Object.assign(existingResidency, action.payload);
      }
    },
    deleteResidency(state, action: PayloadAction<number>) {
      state.residencies = state.residencies.filter((residency) => residency.id !== action.payload);
    },
    ...createFilterReducers<ResidenciesState>(),
  },
  extraReducers: createAsyncExtraReducers(fetchResidencies, "residencies"),
});

export const {
  setResidencies,
  setResidency,
  addResidency,
  updateResidency,
  deleteResidency,
  setColumnFilters,
  setColumnFilter,
  removeColumnFilter,
  clearColumnFilters,
  setSearchBarFilter,
} = residencySlice.actions;

export const selectAllResidencies = (state: RootState) => state.residencies.residencies;
export const selectResidency = (state: RootState, residencyId: number) =>
  state.residencies.residencies.find((residency: Residency) => residency.id === residencyId);
export const selectColumnFilters = (state: RootState) => state.residencies.filters;
export const selectSearchBarFilter = (state: RootState) => state.residencies.searchBarFilter;

export default residencySlice.reducer;
