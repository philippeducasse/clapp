import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Application } from "@/interfaces/entities/Application";
import { RootState } from "../store";
import { applicationApiService } from "@/api/applicationApiService";
import { createFilterReducers, FilterableState } from "../shared/filterReducers";

interface ApplicationsState extends FilterableState {
  applications: Application[];
}

const initialState: ApplicationsState = {
  applications: [],
  filters: [],
  globalFilter: "",
};

export const fetchApplications = createAsyncThunk("applications/fetchApplications", async () => {
  const response = await applicationApiService.getAllApplications();
  return response;
});

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
    addApplication(state, action: PayloadAction<Application>) {
      state.applications.push(action.payload);
    },
    updateApplication(state, action: PayloadAction<Application>) {
      const { id } = action.payload;
      const existingApplication = state.applications.find((application) => application.id === id);
      if (existingApplication) {
        Object.assign(existingApplication, action.payload);
      }
    },
    ...createFilterReducers<ApplicationsState>(),
  },
  extraReducers: (builder) => {
    builder.addCase(fetchApplications.fulfilled, (state, action) => {
      state.applications = action.payload.results;
    });
  },
});

export const {
  setApplications,
  setApplication,
  addApplication,
  updateApplication,
  setColumnFilters,
  setColumnFilter,
  removeColumnFilter,
  clearColumnFilters,
  setGlobalFilter,
} = applicationSlice.actions;

export const selectAllApplications = (state: RootState) => state.applications.applications;
export const selectApplication = (state: RootState, applicationId: number) =>
  state.applications.applications.find(
    (application: Application) => application.id === applicationId
  );
export const selectColumnFilters = (state: RootState) => state.applications.filters;
export const selectGlobalFilter = (state: RootState) => state.applications.globalFilter;

export default applicationSlice.reducer;
