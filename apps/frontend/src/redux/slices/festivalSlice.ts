import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Festival } from "@/interfaces/Festival";
import { RootState } from "../store";
import festivalApiService from "@/api/festivalApiService";

interface FestivalsState {
  festivals: Festival[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: FestivalsState = {
  festivals: [],
  status: "idle",
  error: null,
};

export const fetchFestivals = createAsyncThunk("festivals/fetchFestivals", async () => {
  const response = await festivalApiService.getAllFestivals();
  return response;
});

const festivalSlice = createSlice({
  name: "festivals",
  initialState,
  reducers: {
    setFestivals(state, action: PayloadAction<Festival[]>) {
      state.festivals = action.payload;
    },
    addFestival(state, action: PayloadAction<Festival>) {
      state.festivals.push(action.payload);
    },
    updateFestival(state, action: PayloadAction<Festival>) {
      const { id } = action.payload;
      const existingFestival = state.festivals.find((festival) => festival.id === id);
      if (existingFestival) {
        Object.assign(existingFestival, action.payload);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFestivals.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchFestivals.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.festivals = action.payload;
      })
      .addCase(fetchFestivals.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const { setFestivals, addFestival, updateFestival } = festivalSlice.actions;

export const selectAllFestivals = (state: RootState) => state.festivals.festivals;
export const selectFestivalsStatus = (state: RootState) => state.festivals.status;

export const selectFestivalById = (state: RootState, festivalId: number) =>
  state.festivals.festivals.find((festival) => festival.id === festivalId);

export default festivalSlice.reducer;
