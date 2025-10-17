import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Application } from "@/interfaces/entities/Application";
import { RootState } from "../store";
import { applicationApiService } from "@/api/applicationApiService";

interface ApplicationsState {
  applications: Application[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
  selectedApplication?: Application;
}

const initialState: ApplicationsState = {
  applications: [],
  status: "idle",
  error: null,
  selectedApplication: undefined,
};

export const fetchApplications = createAsyncThunk(
  "applications/fetchApplications",
  async () => {
    const response = await applicationApiService.getAllApplications();
    return response;
  }
);

const applicationSlice = createSlice({
  name: "applications",
  initialState,
  reducers: {
    setApplications(state, action: PayloadAction<Application[]>) {
      state.applications = action.payload;
    },
    setApplication(state, action: PayloadAction<Application>) {
      const existingIndex = state.applications.findIndex(
        (application) => application.id === action.payload.id
      );
      if (existingIndex >= 0) {
        state.applications[existingIndex] = action.payload;
      } else {
        state.applications.push(action.payload);
      }
    },
    setSelectedApplication(state, action: PayloadAction<Application>) {
      state.selectedApplication = action.payload;
    },
    addApplication(state, action: PayloadAction<Application>) {
      state.applications.push(action.payload);
    },
    updateApplication(state, action: PayloadAction<Application>) {
      const { id } = action.payload;
      const existingApplication = state.applications.find(
        (application) => application.id === id
      );
      if (existingApplication) {
        Object.assign(existingApplication, action.payload);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchApplications.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchApplications.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.applications = action.payload;
      })
      .addCase(fetchApplications.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const {
  setApplications,
  setApplication,
  addApplication,
  updateApplication,
  setSelectedApplication,
} = applicationSlice.actions;

export const selectAllApplications = (state: RootState) =>
  state.applications.applications;
export const selectApplicationsStatus = (state: RootState) =>
  state.applications.status;
export const selectApplication = (state: RootState, applicationId: number) =>
  state.applications.applications.find(
    (application: Application) => application.id === applicationId
  );

export default applicationSlice.reducer;
