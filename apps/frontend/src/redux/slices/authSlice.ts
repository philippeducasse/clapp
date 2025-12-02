import { createSlice, PayloadAction, createAsyncThunk } from "@reduxjs/toolkit";
import { Profile } from "@/interfaces/entities/Profile";
import { RootState } from "../store";
import { profileApiService } from "@/api/profileApiService";

interface AuthState {
  profile: Profile | null;
}

const initialState: AuthState = {
  profile: null,
};

export const fetchProfile = createAsyncThunk("profiles/fetchProfile", async () => {
  const response = await profileApiService.get();
  return response;
});

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
    builder.addCase(fetchProfile.fulfilled, (state, action) => {
      state.profile = action.payload;
    });
  },
});

export const { setProfile, updateProfile } = authSlice.actions;

export const selectProfile = (state: RootState) => state.profile.profile;

export default authSlice.reducer;
