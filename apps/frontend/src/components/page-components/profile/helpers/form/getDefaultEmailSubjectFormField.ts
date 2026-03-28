import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";

export const getDefaultEmailSubjectFormField = (): ControlledFormElement[] => [
  {
    label: "Default Email Subject Template",
    fieldName: "defaultEmailSubject",
    type: ControlledFormElementType.TEXT,
    helpText:
      "Set a default template for all email subjects. Use {{firstName}}, {{lastName}}, {{companyName}}, {{organisation}}, and {{currentYear}} as placeholders.",
  },
];
