"use client";

import { Provider } from "react-redux";
import { store } from "@/redux/store";
import { useEffect } from "react";
import { useAppDispatch } from "./hook";
import { Profile } from "@/interfaces/entities/Profile";
import { setProfile } from "./slices/authSlice";

const StoreProvider = ({ children }: { children: React.ReactNode }) => {
  return <Provider store={store}>{children}</Provider>;
};
export default StoreProvider;
