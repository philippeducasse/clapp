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
  addToContacts?: AddToContactsOptions;
}

/**
 * Enables an "Add to contacts?" checkbox for MULTI_EMAIL entries
 * that are not already known contacts.
 */
export interface AddToContactsOptions {
  knownEmails: string[];
  selected: string[];
  onChange: (emails: string[]) => void;
}

export interface SliderOptions {
  min: number;
  max: number;
  step: number;
  labels?: string[];
}
