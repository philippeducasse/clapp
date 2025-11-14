import { Control, FieldErrors, FieldValues } from "react-hook-form";
import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";

export interface ControlledFormFieldsProps<T extends FieldValues> {
  fields: ControlledFormElement[];
  errors: FieldErrors<T>;
  control: Control<T, object>;
  isLoading?: boolean;
  disabled?: boolean;
}
