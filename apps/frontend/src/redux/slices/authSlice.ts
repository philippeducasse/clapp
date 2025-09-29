import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Profile } from "@/interfaces/entities/Profile";
import { RootState } from "../store";
import { profileApiService } from "@/api/profileApiService";

interface AuthState {
  profile: Profile | null;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: AuthState = {
  status: "idle",
  error: null,
  profile: null,
};

export const fetchProfile = createAsyncThunk(
  "profiles/fetchProfile",
  async () => {
    const response = await profileApiService.getProfile();
    return response;
  }
);

const authSlice = createSlice({
  name: "profiles",
  initialState,
  reducers: {
    setProfile(state, action: PayloadAction<Profile>) {
      state.profile = action.payload;
    },
    updateProfile(state, action: PayloadAction<Profile>) {
      if (state.profile) {
        state.profile = { ...state.profile, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProfile.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.profile = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const { setProfile, updateProfile } = authSlice.actions;

export const selectProfileStatus = (state: RootState) => state.profile.status;

export default authSlice.reducer;
