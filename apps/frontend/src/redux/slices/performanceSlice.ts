import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Performance } from "@/interfaces/entities/Performance";
import { RootState } from "../store";
import { performanceApiService } from "@/api/performanceApiService";

interface PerformancesState {
  performances: Performance[];
}

const initialState: PerformancesState = {
  performances: [],
};

export const fetchPerformances = createAsyncThunk(
  "performances/fetchPerformances",
  async (profileId: number) => {
    const response = await performanceApiService.getAll(profileId);
    return response;
  }
);

const performanceSlice = createSlice({
  name: "performances",
  initialState,
  reducers: {
    setPerformances(state, action: PayloadAction<Performance[]>) {
      state.performances = action.payload;
    },
    addPerformance(state, action: PayloadAction<Performance>) {
      state.performances.push(action.payload);
    },
    updatePerformance(state, action: PayloadAction<Performance>) {
      const { id } = action.payload;
      const existingPerformance = state.performances.find((performance) => performance.id === id);
      if (existingPerformance) {
        Object.assign(existingPerformance, action.payload);
      }
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchPerformances.fulfilled, (state, action) => {
      state.performances = action.payload;
    });
  },
});

export const { setPerformances, addPerformance, updatePerformance } = performanceSlice.actions;

export const selectAllPerformances = (state: RootState) => state.performances.performances;
export const selectPerformance = (state: RootState, performanceId: number) =>
  state.performances.performances.find(
    (performance: Performance) => performance.id === performanceId
  );

export default performanceSlice.reducer;
