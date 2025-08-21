import { Festival } from "@/interfaces/Festival";
import { Dispatch, SetStateAction } from "react";

export interface DiffViewProps {
  original: Festival;
  updated: Festival;
  setUpdated: Dispatch<SetStateAction<Festival | undefined>>;
}
