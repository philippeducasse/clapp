import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Venue } from "@/interfaces/entities/Venue";
import { RootState } from "../store";
import { venueApiService } from "@/api/venueApiService";
import { GetAllParams } from "@/interfaces/api/ApiService";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { createFilterReducers, BaseSliceState, createAsyncExtraReducers } from "../shared/sharedReducers";

interface VenuesState extends BaseSliceState {
  venues: Venue[];
}

const initialState: VenuesState = {
  venues: [],
  filters: [],
  searchBarFilter: "",
  loading: false,
  error: null,
};

export const fetchVenues = createAsyncThunk<PaginatedResponse<Venue>, GetAllParams | undefined>(
  "venues/fetchVenues",
  async (params?: GetAllParams) => {
    const response = await venueApiService.getAll(params);
    return response;
  },
);

const venueSlice = createSlice({
  name: "venues",
  initialState,
  reducers: {
    setVenues(state, action: PayloadAction<Venue[]>) {
      state.venues = action.payload;
    },
    setVenue(state, action: PayloadAction<Venue>) {
      const existingIndex = state.venues.findIndex((venue) => venue.id === action.payload.id);
      if (existingIndex >= 0) {
        state.venues[existingIndex] = action.payload;
      } else {
        state.venues.push(action.payload);
      }
    },
    addVenue(state, action: PayloadAction<Venue>) {
      state.venues.push(action.payload);
    },
    updateVenue(state, action: PayloadAction<Venue>) {
      const { id } = action.payload;
      const existingVenue = state.venues.find((venue) => venue.id === id);
      if (existingVenue) {
        Object.assign(existingVenue, action.payload);
      }
    },
    deleteVenue(state, action: PayloadAction<number>) {
      state.venues = state.venues.filter((venue) => venue.id !== action.payload);
    },
    ...createFilterReducers<VenuesState>(),
  },
  extraReducers: createAsyncExtraReducers(fetchVenues, "venues"),
});

export const {
  setVenues,
  setVenue,
  addVenue,
  updateVenue,
  deleteVenue,
  setColumnFilters,
  setColumnFilter,
  removeColumnFilter,
  clearColumnFilters,
  setSearchBarFilter,
} = venueSlice.actions;

export const selectAllVenues = (state: RootState) => state.venues.venues;
export const selectVenue = (state: RootState, venueId: number) =>
  state.venues.venues.find((venue: Venue) => venue.id === venueId);
export const selectColumnFilters = (state: RootState) => state.venues.filters;
export const selectSearchBarFilter = (state: RootState) => state.venues.searchBarFilter;

export default venueSlice.reducer;
