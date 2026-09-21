import { ControlledFormElementType } from "./ControlledFormElementType";
import { Action } from "../Enums";
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
  defaultValue?: string | string[];
  multiple?: boolean;
  action?: Action;
  isRegistration?: boolean;
  sliderOptions?: SliderOptions;
  register?: boolean;
}

export interface SliderOptions {
  min: number;
  max: number;
  step: number;
  labels?: string[];
}
