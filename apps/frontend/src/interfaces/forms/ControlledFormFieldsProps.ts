import { Control, ControllerRenderProps, FieldErrors, FieldValues } from "react-hook-form";
import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export interface ControlledFormFieldsProps<T extends FieldValues> {
  fields: ControlledFormElement[];
  errors: FieldErrors<T>;
  control: Control<T, object>;
  isLoading?: boolean;
  disabled?: boolean;
}

export interface BaseControlledProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

export interface BaseControlledPropsWithLabels extends BaseControlledProps {
  showLabels: boolean;
}

export interface BaseControlledPropsWithOptions extends BaseControlledProps {
  options: SelectOptions[];
}

export interface BaseControlledPropsWithOptionsAndLabels extends BaseControlledPropsWithOptions {
  showLabels: boolean;
}

export interface BaseControlledPropsWithType extends BaseControlledPropsWithLabels {
  type: ControlledFormElementType;
}
