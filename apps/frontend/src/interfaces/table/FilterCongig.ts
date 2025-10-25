import { SelectOptions } from "../forms/ControlledFormElement";
import { FilterType} from "@/interfaces/forms/ControlledFormElementType";

export interface FilterConfig {
  column: string;
  label: string;
  type: FilterType
  options?: SelectOptions[];
  multiple: boolean;
}
