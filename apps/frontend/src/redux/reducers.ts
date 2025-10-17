import { store } from "./store";
import { combineReducers } from "@reduxjs/toolkit";
import festivalsReducer from "./slices/festivalSlice";
import residenciesReducer from "./slices/residencySlice";
import venuesReducer from "./slices/venueSlice";
import authReducer from "./slices/authSlice";
import performanceReducer from "./slices/performanceSlice";
import applicationReducer from "./slices/applicationSlice"

const rootReducer = combineReducers({
  festivals: festivalsReducer,
  residencies: residenciesReducer,
  venues: venuesReducer,
  profile: authReducer,
  performances: performanceReducer,
  applications: applicationReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;
export default rootReducer;
