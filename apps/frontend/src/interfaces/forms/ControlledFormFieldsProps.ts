import { Control, FieldErrors } from "react-hook-form";
import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";

export interface ControlledFormFieldsProps<T> {
  fields: ControlledFormElement[];
  errors: FieldErrors<T>;
  control: Control<T, object>;
  isLoading?: boolean;
  disabled?: boolean;
}
