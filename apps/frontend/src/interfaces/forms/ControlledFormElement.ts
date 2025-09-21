import { ControlledFormElementType } from "./ControlledFormElementType";

export interface SelectOptions {
  label: string;
  value: string;
}

export interface ControlledFormElement {
  fieldName: string;
  label: string;
  helpText?: string;
  type: ControlledFormElementType;
  options?: SelectOptions[];
  placeholder?: string;
  required?: boolean;
  className?: string;
  hidden?: boolean;
}
