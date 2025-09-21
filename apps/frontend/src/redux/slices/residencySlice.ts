import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Residency } from "@/interfaces/entities/Residency";
import { RootState } from "../store";
import { residencyApiService } from "@/api/residencyApiService";

interface ResidenciesState {
  residencies: Residency[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
  selectedResidency?: Residency;
}

const initialState: ResidenciesState = {
  residencies: [],
  status: "idle",
  error: null,
  selectedResidency: undefined,
};

export const fetchResidencies = createAsyncThunk(
  "residencies/fetchResidencies",
  async () => {
    const response = await residencyApiService.getResidencies();
    return response;
  }
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
    setSelectedResidency(state, action: PayloadAction<Residency>) {
      state.selectedResidency = action.payload;
    },
    addResidency(state, action: PayloadAction<Residency>) {
      state.residencies.push(action.payload);
    },
    updateResidency(state, action: PayloadAction<Residency>) {
      const { id } = action.payload;
      const existingResidency = state.residencies.find(
        (residency) => residency.id === id
      );
      if (existingResidency) {
        Object.assign(existingResidency, action.payload);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchResidencies.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchResidencies.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.residencies = action.payload;
      })
      .addCase(fetchResidencies.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const {
  setResidencies,
  setResidency,
  addResidency,
  updateResidency,
  setSelectedResidency,
} = residencySlice.actions;

export const selectAllResidencies = (state: RootState) =>
  state.residencies.residencies;
export const selectResidenciesStatus = (state: RootState) =>
  state.residencies.status;
export const selectResidency = (state: RootState, residencyId: number) =>
  state.residencies.residencies.find(
    (residency) => residency.id === residencyId
  );

export default residencySlice.reducer;
