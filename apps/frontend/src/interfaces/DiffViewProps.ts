import { Festival } from "@/interfaces/entities/Festival";
import { Dispatch, SetStateAction } from "react";

export interface DiffViewProps {
  original: Festival;
  updated: Festival;
  setUpdated: Dispatch<SetStateAction<Festival | undefined>>;
}
