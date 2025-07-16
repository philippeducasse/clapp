import { Control, FieldErrors } from "react-hook-form";
import { ControlledFormElement } from "@/interfaces/ControlledFormElement";

export interface ControlledFormFieldsProps<T> {
  fields: ControlledFormElement[];
  errors: FieldErrors<any>;
  control: Control<T, object> | any;
  isLoading?: boolean;
  disabled?: boolean;
}
