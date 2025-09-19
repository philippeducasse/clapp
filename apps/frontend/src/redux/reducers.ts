import { combineReducers } from "@reduxjs/toolkit";
import festivalsReducer from "./slices/festivalSlice";
import residenciesReducer from "./slices/residencySlice";

const rootReducer = combineReducers({
  festivals: festivalsReducer,
  residencies: residenciesReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export default rootReducer;
