import { ControlledFormElementType } from "./ControlledFormElementType";

export interface ControlledFormElement {
  fieldName: string;
  label: string;
  helpText?: string;
  type: ControlledFormElementType;
  placeholder?: string;
}
