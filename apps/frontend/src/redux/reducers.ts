import { combineReducers } from "@reduxjs/toolkit";
import festivalsReducer from "./slices/festivalSlice";

const rootReducer = combineReducers({
  festivals: festivalsReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export default rootReducer;
