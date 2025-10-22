import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Festival } from "@/interfaces/entities/Festival";
import { RootState } from "../store";
import { festivalApiService } from "@/api/festivalApiService";

interface FestivalsState {
  festivals: Festival[];
}

const initialState: FestivalsState = {
  festivals: [],
};

export const fetchFestivals = createAsyncThunk("festivals/fetchFestivals", async () => {
  const response = await festivalApiService.getAll();
  return response;
});

const festivalSlice = createSlice({
  name: "festivals",
  initialState,
  reducers: {
    setFestivals(state, action: PayloadAction<Festival[]>) {
      state.festivals = action.payload;
    },
    setFestival(state, action: PayloadAction<Festival>) {
      const existingIndex = state.festivals.findIndex(
        (festival) => festival.id === action.payload.id
      );
      if (existingIndex >= 0) {
        state.festivals[existingIndex] = action.payload;
      } else {
        state.festivals.push(action.payload);
      }
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
    deleteFestival(state, action: PayloadAction<number>) {
      state.festivals = state.festivals.filter((festival) => festival.id !== action.payload);
    },
  },

  extraReducers: (builder) => {
    builder.addCase(fetchFestivals.fulfilled, (state, action) => {
      state.festivals = action.payload.results;
    });
  },
});

export const { setFestivals, setFestival, addFestival, updateFestival, deleteFestival } =
  festivalSlice.actions;

export const selectAllFestivals = (state: RootState) => state.festivals.festivals;
export const selectFestival = (state: RootState, festivalId: number) =>
  state.festivals.festivals.find((festival: Festival) => festival.id === festivalId);

export default festivalSlice.reducer;
