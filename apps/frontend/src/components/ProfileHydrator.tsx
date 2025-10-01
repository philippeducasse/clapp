"use client";

import { useEffect } from "react";
import { useAppDispatch } from "@/redux/hook";
import { fetchProfile } from "@/redux/slices/authSlice";

export default function ProfileHydrator() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchProfile());
  }, [dispatch]);

  return null;
}
