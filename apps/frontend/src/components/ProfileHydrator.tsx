"use client";

import { useEffect } from "react";
import { useAppDispatch } from "@/redux/hook";
import { setProfile } from "@/redux/slices/authSlice";
import { Profile } from "@/interfaces/entities/Profile";

export default function ProfileHydrator({ profile }: { profile: Profile }) {
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (profile) dispatch(setProfile(profile));
  }, [dispatch, profile]);

  return null;
}
