"use client";

import { createContext, useContext, ReactNode, useState } from "react";
import { Festival } from "@/interfaces/Festival";

interface FestivalContext {
  festival: Festival;
  setFestival: (festival: Festival) => void;
}

const FestivalContext = createContext<FestivalContext | null>(null);

export const FestivalProvider = ({ children, value }: { children: ReactNode; value: Festival }) => {
  const [festival, setFestival] = useState<Festival>(value);

  return <FestivalContext.Provider value={{ festival, setFestival }}>{children}</FestivalContext.Provider>;
};

export const useFestival = () => {
  const context = useContext(FestivalContext);
  if (!context) {
    throw new Error("useFestival must be used within a FestivalProvider");
  }
  return context;
};
