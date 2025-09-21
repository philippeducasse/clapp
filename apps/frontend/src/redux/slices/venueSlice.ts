import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Venue } from "@/interfaces/entities/Venue";
import { RootState } from "../store";
import { venueApiService } from "@/api/venueApiService";

interface VenuesState {
  venues: Venue[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
  selectedVenue?: Venue;
}

const initialState: VenuesState = {
  venues: [],
  status: "idle",
  error: null,
  selectedVenue: undefined,
};

export const fetchVenues = createAsyncThunk("venues/fetchVenues", async () => {
  const response = await venueApiService.getAllVenues();
  return response;
});

const venueSlice = createSlice({
  name: "venues",
  initialState,
  reducers: {
    setVenues(state, action: PayloadAction<Venue[]>) {
      state.venues = action.payload;
    },
    setVenue(state, action: PayloadAction<Venue>) {
      const existingIndex = state.venues.findIndex(
        (venue) => venue.id === action.payload.id
      );
      if (existingIndex >= 0) {
        state.venues[existingIndex] = action.payload;
      } else {
        state.venues.push(action.payload);
      }
    },
    setSelectedVenue(state, action: PayloadAction<Venue>) {
      state.selectedVenue = action.payload;
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
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchVenues.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchVenues.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.venues = action.payload;
      })
      .addCase(fetchVenues.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const { setVenues, setVenue, addVenue, updateVenue, setSelectedVenue } =
  venueSlice.actions;

export const selectAllVenues = (state: RootState) => state.venues.venues;
export const selectVenuesStatus = (state: RootState) => state.venues.status;
export const selectVenue = (state: RootState, venueId: number) =>
  state.venues.venues.find((venue: Venue) => venue.id === venueId);

export default venueSlice.reducer;
