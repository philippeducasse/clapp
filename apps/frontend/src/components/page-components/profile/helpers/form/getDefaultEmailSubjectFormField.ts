import { EMAIL_PLACEHOLDER_HELP_TEXT } from "@/constants/emailPlaceholders";
import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getDefaultEmailSubjectFormField = (): ControlledFormElement[] => [
  {
    label: "Default Email Subject Template",
    fieldName: "defaultEmailSubject",
    type: ControlledFormElementType.TEXT,
    helpText: EMAIL_PLACEHOLDER_HELP_TEXT,
  },
];
