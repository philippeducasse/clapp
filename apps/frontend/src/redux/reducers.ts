import { combineReducers } from "@reduxjs/toolkit";
import festivalsReducer from "./slices/festivalSlice";
import residenciesReducer from "./slices/residencySlice";
import venuesReducer from "./slices/venueSlice";

const rootReducer = combineReducers({
  festivals: festivalsReducer,
  residencies: residenciesReducer,
  venues: venuesReducer,
  profile: profileReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export default rootReducer;
