import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Performance } from "@/interfaces/entities/Performance";
import { RootState } from "../store";
import { performanceApiService } from "@/api/performanceApiService";

interface PerformancesState {
  performances: Performance[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
  selectedPerformance?: Performance;
}

const initialState: PerformancesState = {
  performances: [],
  status: "idle",
  error: null,
  selectedPerformance: undefined,
};

export const fetchPerformances = createAsyncThunk(
  "performances/fetchPerformances",
  async (profileId: number) => {
    const response = await performanceApiService.getPerformances(profileId);
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
    // setSelectedPerformance(state, action: PayloadAction<Performance>) {
    //   state.selectedPerformance = action.payload;
    // },
    addPerformance(state, action: PayloadAction<Performance>) {
      state.performances.push(action.payload);
    },
    updatePerformance(state, action: PayloadAction<Performance>) {
      const { id } = action.payload;
      const existingPerformance = state.performances.find(
        (performance) => performance.id === id
      );
      if (existingPerformance) {
        Object.assign(existingPerformance, action.payload);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPerformances.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchPerformances.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.performances = action.payload;
      })
      .addCase(fetchPerformances.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const { setPerformances, addPerformance, updatePerformance } =
  performanceSlice.actions;

export const selectAllPerformances = (state: RootState) =>
  state.performances.performances;
export const selectPerformance = (state: RootState, performanceId: number) =>
  state.performances.performances.find(
    (performance: Performance) => performance.id === performanceId
  );

export default performanceSlice.reducer;
