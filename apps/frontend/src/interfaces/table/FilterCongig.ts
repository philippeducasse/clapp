import { SelectOptions } from "../forms/ControlledFormElement";
import { FilterType } from "@/interfaces/forms/ControlledFormElementType";

export interface FilterConfig {
  column: string;
  label: string;
  type: FilterType;
  options?: SelectOptions[];
  multiple?: boolean;
  /** Shown before each active-filter chip value, e.g. "Not" for exclusion filters. */
  chipPrefix?: string;
}

export interface ColumnFilter {
  id: string;
  value: unknown;
}
