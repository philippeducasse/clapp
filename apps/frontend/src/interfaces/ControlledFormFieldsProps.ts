import { Control, FieldErrors } from "react-hook-form";
import { ControlledFormElement } from "@/interfaces/ControlledFormElement";

export interface ControlledFormFieldsProps<T> {
  fields: ControlledFormElement[];
  errors: FieldErrors<T>;
  control: Control<T, object>;
  isLoading?: boolean;
  disabled?: boolean;
}
