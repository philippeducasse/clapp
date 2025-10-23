import { SelectOptions } from "../forms/ControlledFormElement";

export interface FilterConfig {
  column: string;
  label: string;
  type: "string" | "date" | "select" | "boolean" | "number";
  options?: SelectOptions[];
  multiple: boolean;
}
