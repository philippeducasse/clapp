import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Application } from "@/interfaces/entities/Application";
import { Profile } from "@/interfaces/entities/Profile";
import { fetchProfile, setProfile } from "./authSlice";
import { getDefaultFilters } from "@/helpers/defaultFilters";
import { EntityName } from "@/interfaces/Enums";
import { RootState } from "../store";
import { applicationApiService } from "@/api/applicationApiService";
import { GetAllParams } from "@/interfaces/api/ApiService";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import {
  createFilterReducers,
  BaseSliceState,
  createAsyncExtraReducers,
} from "../shared/sharedReducers";

interface ApplicationsState extends BaseSliceState {
  applications: Application[];
}

const initialState: ApplicationsState = {
  applications: [],
  filters: [],
  searchBarFilter: "",
  filtersInitialized: false,
  loading: false,
  error: null,
};

export const fetchApplications = createAsyncThunk<
  PaginatedResponse<Application>,
  GetAllParams | undefined
>("applications/fetchApplications", async (params?: GetAllParams) => {
  const response = await applicationApiService.getAll(params);
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
        (application) => application.id === action.payload.id,
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
      const existingApplication = state.applications.find(
        (application) => application.id === id,
      );
      if (existingApplication) {
        Object.assign(existingApplication, action.payload);
      }
    },
    deleteApplication(state, action: PayloadAction<number>) {
      state.applications = state.applications.filter(
        (application) => application.id !== action.payload,
      );
    },
    ...createFilterReducers<ApplicationsState>(),
  },
  extraReducers: (builder) => {
    // Apply the profile-derived default filters (see helpers/defaultFilters).
    // Only applies while filters are uninitialized, so it never overrides filters
    // the user has changed (e.g. after saving the profile).
    const applyDefaultFilters = (
      state: ApplicationsState,
      action: PayloadAction<Profile>,
    ) => {
      if (state.filtersInitialized) return;
      const defaultFilters = getDefaultFilters(EntityName.APPLICATION, action.payload);
      if (defaultFilters.length === 0) return;
      state.filters = defaultFilters;
      state.filtersInitialized = true;
    };
    builder
      .addCase(fetchProfile.fulfilled, applyDefaultFilters)
      .addCase(setProfile, applyDefaultFilters);
    createAsyncExtraReducers<Application, ApplicationsState, GetAllParams | undefined>(
      fetchApplications,
      "applications",
    )(builder);
  },
});

export const {
  setApplications,
  setApplication,
  addApplication,
  updateApplication,
  deleteApplication,
  setColumnFilters,
  setColumnFilter,
  removeColumnFilter,
  clearColumnFilters,
  setSearchBarFilter,
  initializeColumnFilters,
} = applicationSlice.actions;

export const selectAllApplications = (state: RootState) =>
  state.applications.applications;
export const selectApplication = (state: RootState, applicationId: number) =>
  state.applications.applications.find(
    (application: Application) => application.id === applicationId,
  );
export const selectColumnFilters = (state: RootState) =>
  state.applications.filters;
export const selectSearchBarFilter = (state: RootState) =>
  state.applications.searchBarFilter;

export default applicationSlice.reducer;
